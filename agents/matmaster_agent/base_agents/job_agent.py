import json
import logging
import os
import traceback
from functools import wraps
from typing import AsyncGenerator, Optional, Union, override

import aiohttp
import jsonpickle
import requests
from dp.agent.adapter.adk import CalculationMCPTool
from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.agents.llm_agent import AfterToolCallback, BeforeToolCallback
from google.adk.events import Event, EventActions
from google.adk.tools import BaseTool, ToolContext, transfer_to_agent
from mcp.types import CallToolResult
from pydantic import Field

from agents.matmaster_agent.base_agents.io_agent import (
    HandleFileUploadLlmAgent,
)
from agents.matmaster_agent.constant import (
    BOHRIUM_API_URL,
    CURRENT_ENV,
    FRONTEND_STATE_KEY,
    JOB_LIST_KEY,
    JOB_RESULT_KEY,
    LOADING_DESC,
    LOADING_END,
    LOADING_START,
    LOADING_STATE_KEY,
    LOADING_TITLE,
    OPENAPI_HOST,
    TMP_FRONTEND_STATE_KEY,
    ModelRole,
    Transfer2Agent,
    get_BohriumExecutor,
    get_BohriumStorage,
    get_DFlowExecutor,
)
from agents.matmaster_agent.model import BohrJobInfo, DFlowJobInfo
from agents.matmaster_agent.prompt import (
    ResultCoreAgentDescription,
    SubmitRenderAgentDescription,
)
from agents.matmaster_agent.utils import (
    all_text_event,
    context_function_event,
    context_text_event,
    frontend_text_event,
    is_function_call,
    is_function_response,
    is_text,
    is_text_and_not_bohrium,
    parse_result,
    send_error_event,
    update_session_state,
)

logger = logging.getLogger(__name__)


async def default_before_tool_callback(tool, args, tool_context):
    return


async def default_after_tool_callback(tool, args, tool_context, tool_response):
    return


# 总应该在最后
def catch_tool_call_error(func: BeforeToolCallback) -> BeforeToolCallback:
    @wraps(func)
    async def wrapper(tool: BaseTool, args: dict, tool_context: ToolContext) -> dict:
        # 两步操作：
        # 1. 调用被装饰的 before_tool_callback；
        # 2. 如果调用的 before_tool_callback 有返回值，以这个为准
        try:
            if (before_tool_result := await func(tool, args, tool_context)) is not None:
                return before_tool_result

            return await tool.run_async(args=args, tool_context=tool_context)
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "error_type": type(e).__name__,
                "treceback": traceback.format_exc()
            }

    return wrapper


def check_job_create(func: BeforeToolCallback) -> BeforeToolCallback:
    @wraps(func)
    async def wrapper(tool: BaseTool, args: dict, tool_context: ToolContext) -> Optional[dict]:
        # 两步操作：
        # 1. 调用被装饰的 before_tool_callback；
        # 2. 如果调用的 before_tool_callback 有返回值，以这个为准
        if (before_tool_result := await func(tool, args, tool_context)) is not None:
            return before_tool_result

        # 如果 tool 不是 CalculationMCPTool，不应该调用这个 callback
        if not isinstance(tool, CalculationMCPTool):
            return {"status": "error", "msg": "Current tool can't create job!"}

        if tool.executor is not None:
            url = f"{OPENAPI_HOST}/openapi/v1/job/create"
            payload = {'projectId': int(tool_context.state['project_id']), 'name': 'check_job_create'}
            params = {'accessKey': tool_context.state['ak']}

            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, params=params) as response:
                    res = json.loads(await response.text())
                    if res['code'] != 0:
                        return res

    return wrapper


def _get_ak(ctx: Union[InvocationContext, ToolContext], executor, storage):
    session_state = ctx.session.state if isinstance(ctx, InvocationContext) else ctx.state
    access_key = session_state[FRONTEND_STATE_KEY]['biz'].get('ak', None)
    if access_key is None:
        access_key = os.getenv("BOHRIUM_ACCESS_KEY", None)
    if access_key is not None:
        if executor is not None:
            if executor['type'] == "dispatcher":  # BohriumExecutor
                executor['machine']['remote_profile']['access_key'] = access_key
            elif executor["type"] == "local" and executor.get("dflow", False):  # DFlowExecutor
                executor['env']['BOHRIUM_ACCESS_KEY'] = access_key
        if storage is not None:  # BohriumStorage
            storage['plugin']['access_key'] = access_key
    return access_key, executor, storage


def _get_projectId(ctx: Union[InvocationContext, ToolContext], executor, storage):
    session_state = ctx.session.state if isinstance(ctx, InvocationContext) else ctx.state
    project_id = session_state[FRONTEND_STATE_KEY]['biz'].get('projectId', None)
    if project_id is None:
        project_id = os.getenv("BOHRIUM_PROJECT_ID", None)
    if project_id is not None:
        if executor is not None:
            if executor['type'] == "dispatcher":  # BohriumExecutor
                executor['machine']['remote_profile']['project_id'] = int(project_id)
                # Redundant set for resources/envs keys
                executor["resources"] = executor.get("resources", {})
                executor["resources"]["envs"] = executor["resources"].get("envs", {})
                executor["resources"]["envs"]["BOHRIUM_PROJECT_ID"] = int(project_id)
            elif executor["type"] == "local" and executor.get("dflow", False):  # DFlowExecutor
                executor['env']['BOHRIUM_PROJECT_ID'] = str(project_id)
        if storage is not None:  # BohriumStorage
            storage['plugin']['project_id'] = int(project_id)
    return project_id, executor, storage


def ak_to_username(access_key: str) -> str:
    url = f"{OPENAPI_HOST}/openapi/v1/account/info"
    headers = {
        "AccessKey": access_key,
        "User-Agent": "Apifox/1.0.0 (https://apifox.com)",
        "Accept": "*/*",
        "Host": f"{OPENAPI_HOST.split('//')[1]}",
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # 抛出HTTP错误异常

        data = response.json()
        if data.get("code") == 0:
            user_data = data.get("data", {})
            email = user_data.get("email", "")
            phone = user_data.get("phone", "")
            if not email and not phone:
                raise ValueError(
                    "Username not found in response. Please bind your email or phone at https://www.bohrium.com/settings/user.")
            username = email if email else phone
            return username
        else:
            raise Exception(f"API error: {data}")
    except requests.RequestException as e:
        raise Exception(f"HTTP request failed: {e}")
    except Exception as e:
        raise Exception(f"Failed to get user info: {e}")


def _get_username(ctx: Union[InvocationContext, ToolContext], executor):
    access_key, _, _ = _get_ak(ctx, executor=None, storage=None)
    if not access_key:
        raise ValueError("AccessKey not found")
    username = ak_to_username(access_key=access_key)
    if username:
        if executor is not None:
            if executor['type'] == "dispatcher":  # BohriumExecutor
                # Redundant set for resources/envs keys
                executor["resources"] = executor.get("resources", {})
                executor["resources"]["envs"] = executor["resources"].get("envs", {})
                executor['resources']['envs']['BOHRIUM_USERNAME'] = \
                    str(username)
            elif executor["type"] == "local" and executor.get("dflow", False):  # DFlowExecutor
                executor['env']['BOHRIUM_USERNAME'] = str(username)
    return username, executor


def ak_to_ticket(
        access_key: str,
        expiration: int = 48  # 48 hours
) -> str:
    # if CurrentEnv == "uat":
    #     BOHRIUM_API_URL = "https://bohrium-api.uat.dp.tech"
    # elif CurrentEnv == "test":
    #     BOHRIUM_API_URL = "https://bohrium-api.test.dp.tech"
    # else:
    #     BOHRIUM_API_URL = "https://bohrium-api.dp.tech"
    url = f"{BOHRIUM_API_URL}/bohrapi/v1/ticket/get?expiration={expiration}&preOrderId=0"
    headers = {
        "Brm-AK": access_key,
        "User-Agent": "Apifox/1.0.0 (https://apifox.com)",
        "Accept": "*/*",
        "Host": f"{BOHRIUM_API_URL.split('//')[1]}",
        "Connection": "keep-alive"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data.get("code") == 0:
            ticket = data.get("data", {}).get("ticket", "")
            if not ticket:
                raise ValueError("Ticket not found in response.")
            return ticket
        else:
            raise Exception(f"API error: {data}")
    except requests.RequestException as e:
        raise Exception(f"HTTP request failed: {e}")
    except Exception as e:
        raise Exception(f"Failed to get ticket: {e}")


def _get_ticket(ctx: Union[InvocationContext, ToolContext], executor):
    access_key, _, _ = _get_ak(ctx, executor=None, storage=None)
    if not access_key:
        raise ValueError("AccessKey not found")
    ticket = ak_to_ticket(access_key=access_key)
    if ticket:
        if executor is not None:
            if executor['type'] == "dispatcher":  # BohriumExecutor
                # Redundant set for resources/envs keys
                executor["resources"] = executor.get("resources", {})
                executor["resources"]["envs"] = executor["resources"].get("envs", {})
                executor['resources']['envs']['BOHRIUM_TICKET'] = str(ticket)
            elif executor["type"] == "local" and executor.get("dflow", False):  # DFlowExecutor
                executor['env']['BOHRIUM_TICKET'] = str(ticket)
    return ticket, executor


def _get_current_env(executor):
    if CURRENT_ENV:
        current_env = CURRENT_ENV
    else:
        current_env = "prod"
    if executor is not None:
        if executor['type'] == "dispatcher":  # BohriumExecutor
            # Redundant set for resources/envs keys
            executor["resources"] = executor.get("resources", {})
            executor["resources"]["envs"] = executor["resources"].get("envs", {})
            executor['resources']['envs']['CURRENT_ENV'] = str(CURRENT_ENV)
        elif executor["type"] == "local" and executor.get("dflow", False):  # DFlowExecutor
            executor['env']['CURRENT_ENV'] = str(CURRENT_ENV)
    return current_env, executor


def get_ak_projectId(func: BeforeToolCallback) -> BeforeToolCallback:
    @wraps(func)
    async def wrapper(tool: BaseTool, args: dict, tool_context: ToolContext) -> Optional[dict]:
        # 两步操作：
        # 1. 调用被装饰的 before_tool_callback；
        # 2. 如果调用的 before_tool_callback 有返回值，以这个为准
        if (before_tool_result := await func(tool, args, tool_context)) is not None:
            return before_tool_result

        # 如果 tool 为 Transfer2Agent，不做 ak 和 project_id 设置/校验
        if tool.name == Transfer2Agent:
            return None

        # 如果 tool 不是 CalculationMCPTool，不应该调用这个 callback
        if not isinstance(tool, CalculationMCPTool):
            return {"status": "error", "msg": "Current tool does not have <storage>"}

        # 获取 access_key
        access_key, tool.executor, tool.storage = _get_ak(tool_context, tool.executor, tool.storage)
        if access_key is None:
            return {"status": "error", "msg": "AccessKey was not provided"}

        # 获取 project_id
        try:
            project_id, tool.executor, tool.storage = _get_projectId(tool_context, tool.executor, tool.storage)
        except ValueError:
            return {"status": "error", "msg": f"ProjectId is invalid"}
        if project_id is None:
            return {"status": "error", "msg": "ProjectId was not provided. Please select the project first."}

        tool_context.state['ak'] = access_key
        tool_context.state['project_id'] = project_id

    return wrapper


def set_dpdispatcher_env(func: BeforeToolCallback) -> BeforeToolCallback:
    @wraps(func)
    async def wrapper(tool: BaseTool, args: dict, tool_context: ToolContext) -> Optional[dict]:
        # 先执行前面的回调链
        if (before_tool_result := await func(tool, args, tool_context)) is not None:
            return before_tool_result
        try:
            # 注入 username
            _, tool.executor = _get_username(tool_context, tool.executor)
        except Exception as e:
            return {"status": "error", "msg": f"Failed to get username: {str(e)}"}

        # 注入 ticket
        try:
            _, tool.executor = _get_ticket(tool_context, tool.executor)
        except Exception as e:
            return {"status": "error", "msg": f"Failed to get ticket: {str(e)}"}

        # 注入当前环境
        try:
            _, tool.executor = _get_current_env(tool.executor)
        except Exception as e:
            return {
                "status": "error",
                "msg": f"Failed to get current environment: {str(e)}"
            }

    return wrapper


def check_tool_response(func: AfterToolCallback) -> AfterToolCallback:
    """A decorator that checks the tool response type before executing the callback function.

    This decorator wraps an AfterToolCallback function and checks if the tool_response
    is a dictionary. If it is, the wrapper returns None without calling the original
    function. Otherwise, it proceeds with the original function.

    Args:
        func: The AfterToolCallback function to be wrapped.

    Returns:
        AfterToolCallback: The wrapped function that includes the type checking logic.

    The wrapper function parameters:
        tool: The BaseTool instance that was executed.
        args: Dictionary of arguments passed to the tool.
        tool_context: The context in which the tool was executed.
        tool_response: The response from the tool, either a dict or CallToolResult.

    Returns:
        Optional[dict]: Returns None if tool_response is a dict, otherwise returns
        the result of the original callback function.
    """

    @wraps(func)
    async def wrapper(tool: BaseTool, args: dict, tool_context: ToolContext,
                      tool_response: Union[dict, CallToolResult]) -> Optional[dict]:
        if type(tool_response) is dict:
            return

        return await func(tool, args, tool_context, tool_response)

    return wrapper


class CalculationMCPLlmAgent(HandleFileUploadLlmAgent):
    """An LLM agent specialized for calculation tasks with built-in error handling and project ID management.

    Extends the HandleFileUploadLlmAgent with additional features:
    - Automatic error handling for tool calls
    - Project ID retrieval before tool execution
    - OpikTracer integration for comprehensive operation tracing

    Note: User-provided callbacks will execute before the built-in OpikTracer callbacks.

    Attributes:
        Inherits all attributes from LlmAgent.
    """

    loading: bool = Field(False, description="Whether the agent is in loading state", exclude=True)

    def __init__(self, model, name, instruction='', description='', sub_agents=None,
                 global_instruction='', tools=None, output_key=None,
                 before_agent_callback=None, before_model_callback=None,
                 before_tool_callback=default_before_tool_callback, after_tool_callback=default_after_tool_callback,
                 after_model_callback=None, after_agent_callback=None, loading=False,
                 disallow_transfer_to_parent=False):
        """Initialize a CalculationLlmAgent with enhanced tool call capabilities.

        Args:
            model: The language model instance to be used by the agent
            name: Unique identifier for the agent
            instruction: Primary instruction guiding the agent's behavior
            description: Optional detailed description of the agent (default: '')
            sub_agents: List of subordinate agents (default: None)
            global_instruction: Instruction applied across all agent operations (default: '')
            tools: Tools available to the agent (default: None)
            output_key: Key for identifying the agent's output (default: None)
            before_agent_callback: Callback executed before agent runs (default: None)
            before_model_callback: Callback executed before model inference (default: None)
            before_tool_callback: Callback executed before tool execution
                                (default: default_before_tool_callback)
            after_tool_callback: Callback executed after tool execution (default: None)
            after_model_callback: Callback executed after model inference (default: None)
            after_agent_callback: Callback executed after agent completes (default: None)

        Implementation Notes:
            1. Wraps the before_tool_callback with:
               - Error handling (catch_tool_call_error)
               - Project ID retrieval (get_ak_projectId)
            2. Maintains callback execution order: user callbacks → OpikTracer callbacks
            3. Designed specifically for calculation-intensive MCP workflows
        """

        # Todo: support List[before_tool_callback]
        before_tool_callback = catch_tool_call_error(
            check_job_create(
                set_dpdispatcher_env(
                    get_ak_projectId(
                        before_tool_callback
                    )
                )
            )
        )
        after_tool_callback = check_tool_response(after_tool_callback)

        super().__init__(
            model=model,
            name=name,
            description=description,
            instruction=instruction,
            global_instruction=global_instruction,
            sub_agents=sub_agents or [],
            tools=tools or [],
            output_key=output_key,
            before_agent_callback=before_agent_callback,
            before_model_callback=before_model_callback,
            before_tool_callback=before_tool_callback,
            after_tool_callback=after_tool_callback,
            after_model_callback=after_model_callback,
            after_agent_callback=after_agent_callback,
            disallow_transfer_to_parent=disallow_transfer_to_parent
        )

        self.loading = loading

    # Execution Order: user_question -> chembrain_llm -> event -> user_agree_transfer -> retrosyn_llm (param) -> event
    #                  -> user_agree_param -> retrosyn_llm (function_call) -> event -> tool_call
    #                  -> retrosyn_llm (function_response) -> event
    @override
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        try:
            async for event in super()._run_async_impl(ctx):
                if self.loading:
                    if is_function_call(event):
                        loading_title_msg = f"正在调用 {event.content.parts[0].function_call.name}..."
                        loading_desc_msg = f"结果生成中，请稍等片刻..."
                        logger.info(loading_title_msg)
                        yield Event(
                            author=self.name,
                            actions=EventActions(state_delta={TMP_FRONTEND_STATE_KEY: {LOADING_STATE_KEY: LOADING_START,
                                                                                       LOADING_TITLE: loading_title_msg,
                                                                                       LOADING_DESC: loading_desc_msg}}))
                    elif is_function_response(event):
                        logger.info(f"{event.content.parts[0].function_response.name} 调用结束")
                        yield Event(
                            author=self.name,
                            actions=EventActions(state_delta={TMP_FRONTEND_STATE_KEY: {LOADING_STATE_KEY: LOADING_END}})
                        )
                yield event
        except BaseExceptionGroup as err:
            from agents.matmaster_agent.agent import (
                root_agent as matmaster_agent,
            )

            async for error_event in send_error_event(err, ctx, self.name, matmaster_agent):
                yield error_event


class SubmitCoreCalculationMCPLlmAgent(CalculationMCPLlmAgent):
    @override
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        logger.info(f"[{self.name}] state: {ctx.session.state}")

        try:
            async for event in super()._run_async_impl(ctx):
                if event.long_running_tool_ids:
                    ctx.session.state['long_running_ids'] += event.long_running_tool_ids
                    await update_session_state(ctx, self.name)

                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if (
                                part
                                and part.function_response
                                and part.function_response.id in ctx.session.state['long_running_ids']
                                and "result" in part.function_response.response
                                and not part.function_response.response["result"].isError
                        ):
                            raw_result = part.function_response.response["result"]
                            results = json.loads(raw_result.content[0].text)
                            origin_job_id = results["job_id"]
                            job_name = part.function_response.name
                            job_status = results['status']
                            if not ctx.session.state["dflow"]:
                                bohr_job_id = results['extra_info']["bohr_job_id"]
                                job_detail_url = results['extra_info']['job_link']
                                frontend_result = BohrJobInfo(origin_job_id=origin_job_id, job_name=job_name,
                                                              job_status=job_status, job_detail_url=job_detail_url,
                                                              job_id=bohr_job_id).model_dump(mode="json")
                            else:
                                workflow_id = results['extra_info']['workflow_id']
                                workflow_uid = results['extra_info']['workflow_uid']
                                workflow_url = results['extra_info']['workflow_link']
                                frontend_result = DFlowJobInfo(origin_job_id=origin_job_id, job_name=job_name,
                                                               job_status=job_status, workflow_id=workflow_id,
                                                               workflow_uid=workflow_uid,
                                                               workflow_url=workflow_url).model_dump(mode="json")
                            ctx.session.state['long_running_jobs'][origin_job_id] = frontend_result
                            ctx.session.state["render_job_list"] = True
                            ctx.session.state["render_job_id"].append(origin_job_id)
                            ctx.session.state['long_running_jobs_count'] += 1
                            await update_session_state(ctx, self.name)

                # Send Normal LlmResponse to Frontend, function_call -> function_response -> Llm_response
                if is_text(event):
                    for function_event in context_function_event(ctx, self.name, "system_submit_core_info",
                                                                 {"msg": event.content.parts[0].text},
                                                                 ModelRole):
                        yield function_event
                else:
                    yield event
        except BaseExceptionGroup as err:
            async for error_event in send_error_event(err, ctx, self.name,
                                                      ctx.agent.parent_agent.parent_agent.parent_agent):
                yield error_event


class SubmitRenderAgent(LlmAgent):

    def __init__(self, **kwargs):
        super().__init__(description=SubmitRenderAgentDescription, **kwargs)

    @override
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        logger.info(f"[{self.name}] state: {ctx.session.state}")
        try:
            async for event in super()._run_async_impl(ctx):
                if is_text(event) and ctx.session.state["render_job_list"]:
                    for cur_render_job_id in ctx.session.state["render_job_id"]:
                        # Render Frontend Job-List Component
                        job_list_comp_data = {
                            "eventType": 1,
                            "eventData": {
                                "contentType": 1,
                                "renderType": '@bohrium-chat/matmodeler/task-message',
                                "content": {
                                    JOB_LIST_KEY: ctx.session.state['long_running_jobs'][cur_render_job_id]
                                },
                            }
                        }
                        if not ctx.session.state["dflow"]:
                            # 同时发送流式消息（聊条的时候可见）和数据库消息（历史记录的时候可见）
                            for event in all_text_event(ctx=ctx,
                                                        author=self.name,
                                                        text=f"<bohrium-chat-msg>{json.dumps(job_list_comp_data)}</bohrium-chat-msg>",
                                                        role=ModelRole):
                                yield event

                    ctx.session.state["render_job_list"] = False
                    ctx.session.state["render_job_id"] = []
                    await update_session_state(ctx, self.name)
        except BaseExceptionGroup as err:
            async for error_event in send_error_event(err, ctx, self.name,
                                                      ctx.agent.parent_agent.parent_agent.parent_agent):
                yield error_event


class SubmitValidator(LlmAgent):
    @override
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        if ctx.session.state["long_running_jobs_count"] > ctx.session.state["long_running_jobs_count_ori"]:
            submit_validator_msg = "The Job has indeed been submitted."
            ctx.session.state["long_running_jobs_count_ori"] = ctx.session.state["long_running_jobs_count"]
            await update_session_state(ctx, self.name)
        else:
            submit_validator_msg = "No Job Submitted."

        for function_event in context_function_event(ctx, self.name, "system_submit_validator",
                                                     {"msg": submit_validator_msg},
                                                     ModelRole):
            yield function_event


class ResultCalculationMCPLlmAgent(CalculationMCPLlmAgent):

    def __init__(self, **kwargs):
        super().__init__(description=ResultCoreAgentDescription, **kwargs)

    @override
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        logger.info(f"[{self.name}] state: {ctx.session.state}")
        try:
            await self.tools[0].get_tools()
            if not ctx.session.state["dflow"]:
                access_key, Executor, BohriumStorge = _get_ak(ctx, get_BohriumExecutor(), get_BohriumStorage())
                project_id, Executor, BohriumStorge = _get_projectId(ctx, Executor, BohriumStorge)
            else:
                access_key, Executor, BohriumStorge = _get_ak(ctx, get_DFlowExecutor(), get_BohriumStorage())
                project_id, Executor, BohriumStorge = _get_projectId(ctx, Executor, BohriumStorge)

            for origin_job_id in list(ctx.session.state['long_running_jobs'].keys()):
                # 如果该任务结果已经在上下文中 && 用户没有请求这个任务结果，则不再重复查询
                if (
                        ctx.session.state['long_running_jobs'][origin_job_id]['job_in_ctx'] and
                        origin_job_id != ctx.session.state[FRONTEND_STATE_KEY]["biz"].get("origin_id", None)
                ):
                    continue

                if self.tools[0].query_tool is None:
                    yield context_text_event(ctx, self.name, f"Query Tool is None, Failed", ModelRole)
                    break

                query_res = await self.tools[0].query_tool.run_async(
                    args={"job_id": origin_job_id, "executor": Executor}, tool_context=None)
                if query_res.isError:
                    logger.error(query_res.content[0].text)
                    continue
                status = query_res.content[0].text
                if status != "Running":
                    ctx.session.state['long_running_jobs'][origin_job_id]['job_status'] = status
                    results_res = await self.tools[0].results_tool.run_async(
                        args={"job_id": origin_job_id, "executor": Executor, "storage": BohriumStorge},
                        tool_context=None)
                    if results_res.isError:  # Job Failed
                        err_msg = results_res.content[0].text
                        if err_msg.startswith("Error executing tool"):
                            err_msg = err_msg[err_msg.find(":") + 2:]
                        yield frontend_text_event(ctx, self.name, f"Job {origin_job_id} failed: {err_msg}",
                                                  ModelRole)
                    else:  # Job Success
                        raw_result = results_res.content[0].text
                        dict_result = jsonpickle.loads(raw_result)
                        ctx.session.state['long_running_jobs'][origin_job_id]['job_result'] = await parse_result(
                            dict_result)

                        # Render Frontend Job-Result Component
                        job_result_comp_data = {
                            "eventType": 1,
                            "eventData": {
                                "contentType": 1,
                                "renderType": '@bohrium-chat/matmodeler/dialog-file',
                                "content": {
                                    JOB_RESULT_KEY: ctx.session.state['long_running_jobs'][origin_job_id][
                                        'job_result']
                                },
                            }
                        }

                        # Only for debug
                        if os.getenv("MODE", None) == "debug":
                            ctx.session.state[FRONTEND_STATE_KEY]["biz"]["origin_id"] = origin_job_id

                        # 如果用户请求这个id的任务结果，渲染前端组件
                        if origin_job_id == ctx.session.state[FRONTEND_STATE_KEY]["biz"].get("origin_id", None):
                            for event in all_text_event(ctx,
                                                        self.name,
                                                        f"<bohrium-chat-msg>{json.dumps(job_result_comp_data)}</bohrium-chat-msg>",
                                                        ModelRole):
                                yield event

                            # Only for debug
                            if os.getenv("MODE", None) == "debug":
                                ctx.session.state[FRONTEND_STATE_KEY]["biz"]["origin_id"] = None

                        # 包装成function_call，来避免在历史记录中展示；同时模型可以在上下文中感知
                        for event in context_function_event(ctx, self.name, "system_job_result",
                                                            job_result_comp_data['eventData']['content'],
                                                            ModelRole):
                            yield event

                        ctx.session.state['long_running_jobs'][origin_job_id]['job_in_ctx'] = True
                    await update_session_state(ctx, self.name)

                # 包装成function_call，来避免在历史记录中展示；同时模型可以在上下文中感知
                for event in context_function_event(ctx, self.name, "system_job_status",
                                                    {"msg": f"Job {origin_job_id} status is {status}"},
                                                    ModelRole):
                    yield event
            yield Event(author=self.name)
        except BaseExceptionGroup as err:
            async for error_event in send_error_event(err, ctx, self.name,
                                                      ctx.agent.parent_agent.parent_agent.parent_agent):
                yield error_event


class ResultTransferLlmAgent(LlmAgent):
    @override
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        async for event in super()._run_async_impl(ctx):
            # Send Normal LlmResponse to Frontend, function_call -> function_response -> Llm_response
            if is_text_and_not_bohrium(event):
                for function_event in context_function_event(ctx, self.name,
                                                             "system_result_transfer_info",
                                                             {"response": event.content.parts[0].text},
                                                             ModelRole):
                    yield function_event
            else:
                yield event


class BaseAsyncJobAgent(LlmAgent):
    submit_agent: SequentialAgent
    result_agent: SequentialAgent
    # transfer_agent: LlmAgent
    dflow_flag: False = Field(False, description="Whether the agent is dflow related", exclude=True)
    supervisor_agent: str

    def __init__(
            self,
            model,
            agent_name: str,
            agent_description: str,
            agent_instruction: str,
            submit_core_agent_class,
            submit_core_agent_name: str,
            submit_core_agent_description: str,
            submit_core_agent_instruction: str,
            mcp_tools: list,
            submit_render_agent_name: str,
            result_core_agent_class,
            result_core_agent_name: str,
            result_core_agent_instruction: str,
            result_transfer_agent_name: str,
            result_transfer_agent_instruction: str,
            transfer_agent_name: str,
            transfer_agent_instruction: str,
            submit_agent_name: str,
            submit_agent_description: str,
            result_agent_name: str,
            result_agent_description: str,
            dflow_flag: bool,
            supervisor_agent: str
    ):
        # 创建提交核心代理
        submit_core_agent = submit_core_agent_class(
            model=model,
            name=submit_core_agent_name,
            description=submit_core_agent_description,
            instruction=submit_core_agent_instruction,
            tools=mcp_tools,
            disallow_transfer_to_parent=True
        )

        # 创建提交渲染代理
        submit_render_agent = SubmitRenderAgent(
            model=model,
            name=submit_render_agent_name
        )

        submit_validator_agent = SubmitValidator(
            model=model,
            name="submit_validator_agent"
        )

        # 创建提交序列代理
        submit_agent = SequentialAgent(
            name=submit_agent_name,
            description=submit_agent_description,
            sub_agents=[submit_core_agent, submit_render_agent, submit_validator_agent]
        )

        # 创建结果核心代理
        result_core_agent = result_core_agent_class(
            model=model,
            name=result_core_agent_name,
            tools=mcp_tools,
            instruction=result_core_agent_instruction
        )

        # 创建结果转移代理
        result_transfer_agent = ResultTransferLlmAgent(
            model=model,
            name=result_transfer_agent_name,
            instruction=result_transfer_agent_instruction,
            tools=[transfer_to_agent]
        )

        # 创建结果序列代理
        result_agent = SequentialAgent(
            name=result_agent_name,
            description=result_agent_description,
            # sub_agents=[result_core_agent, result_transfer_agent]
            sub_agents=[result_core_agent]
        )

        # # 创建转移代理
        # transfer_agent = LlmAgent(
        #     model=llm_config.gpt_4o,
        #     name=transfer_agent_name,
        #     description=TransferAgentDescription,
        #     instruction=transfer_agent_instruction
        # )

        # 初始化父类
        super().__init__(
            name=agent_name,
            model=model,
            description=agent_description,
            instruction=agent_instruction,
            submit_agent=submit_agent,
            result_agent=result_agent,
            # transfer_agent=transfer_agent,
            dflow_flag=dflow_flag,
            # sub_agents=[submit_agent, result_agent, transfer_agent],
            sub_agents=[submit_agent, result_agent],
            supervisor_agent=supervisor_agent
        )

    @override
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        ctx.session.state["dflow"] = self.dflow_flag
        await update_session_state(ctx, self.name)

        if ctx.session.state[FRONTEND_STATE_KEY]["biz"].get("origin_id", None) is not None:
            async for result_event in self.result_agent.run_async(ctx):
                yield result_event
        else:
            async for result_event in self.result_agent.run_async(ctx):
                yield result_event

            async for submit_event in self.submit_agent.run_async(ctx):
                yield submit_event

            # async for transfer_event in self.transfer_agent.run_async(ctx):
            #     yield transfer_event

        for function_event in context_function_event(ctx, self.name, "transfer_to_agent", None, ModelRole,
                                                     {"agent_name": self.supervisor_agent}):
            yield function_event
