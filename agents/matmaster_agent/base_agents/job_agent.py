import json
import logging
import os
from typing import AsyncGenerator, override

import jsonpickle
from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event, EventActions
from google.adk.tools import transfer_to_agent
from pydantic import Field

from agents.matmaster_agent.base_agents.callback import check_tool_response, default_before_tool_callback, \
    catch_tool_call_error, check_job_create, set_dpdispatcher_env, get_ak_projectId, default_after_tool_callback, \
    _get_ak, _get_projectId, tgz_oss_to_oss_list
from agents.matmaster_agent.base_agents.io_agent import (
    HandleFileUploadLlmAgent,
)
from agents.matmaster_agent.constant import (
    FRONTEND_STATE_KEY,
    JOB_LIST_KEY,
    JOB_RESULT_KEY,
    LOADING_DESC,
    LOADING_END,
    LOADING_START,
    LOADING_STATE_KEY,
    LOADING_TITLE,
    TMP_FRONTEND_STATE_KEY,
    ModelRole,
    get_BohriumExecutor,
    get_BohriumStorage,
    get_DFlowExecutor,
)
from agents.matmaster_agent.model import BohrJobInfo, DFlowJobInfo
from agents.matmaster_agent.prompt import (
    ResultCoreAgentDescription,
    SubmitRenderAgentDescription, gen_submit_core_agent_description, gen_submit_core_agent_instruction,
    gen_result_core_agent_instruction, gen_submit_agent_description, gen_result_agent_description,
)
from agents.matmaster_agent.utils.event_utils import is_function_call, is_function_response, send_error_event, is_text, \
    context_function_event, all_text_event, context_text_event, frontend_text_event, is_text_and_not_bohrium
from agents.matmaster_agent.utils.helper_func import update_session_state, parse_result

logger = logging.getLogger(__name__)


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
        after_tool_callback = check_tool_response(tgz_oss_to_oss_list(after_tool_callback))

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


class SubmitValidatorAgent(LlmAgent):
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
            mcp_tools: list,
            dflow_flag: bool,
            supervisor_agent: str
    ):
        agent_prefix = agent_name.replace("_agent", "")

        # 创建提交核心代理
        submit_core_agent = SubmitCoreCalculationMCPLlmAgent(
            model=model,
            name=f"{agent_prefix}_submit_core_agent",
            description=gen_submit_core_agent_description(agent_prefix),
            instruction=gen_submit_core_agent_instruction(agent_prefix),
            tools=mcp_tools,
            disallow_transfer_to_parent=True
        )

        # 创建提交渲染代理
        submit_render_agent = SubmitRenderAgent(
            model=model,
            name=f"{agent_prefix}_submit_render_agent"
        )

        submit_validator_agent = SubmitValidatorAgent(
            model=model,
            name=f"{agent_prefix}_submit_validator_agent"
        )

        # 创建提交序列代理
        submit_agent = SequentialAgent(
            name=f"{agent_prefix}_submit_agent",
            description=gen_submit_agent_description(agent_prefix),
            sub_agents=[submit_core_agent, submit_render_agent, submit_validator_agent]
        )

        # 创建结果核心代理
        result_core_agent = ResultCalculationMCPLlmAgent(
            model=model,
            name=f"{agent_prefix}_result_core_agent",
            tools=mcp_tools,
            instruction=gen_result_core_agent_instruction(agent_prefix)
        )

        # 创建结果转移代理
        result_transfer_agent = ResultTransferLlmAgent(
            model=model,
            name=f"{agent_prefix}_result_transfer_agent",
            instruction="result_transfer_agent_instruction",
            tools=[transfer_to_agent]
        )

        # 创建结果序列代理
        result_agent = SequentialAgent(
            name=f"{agent_prefix}_result_agent",
            description=gen_result_agent_description(),
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
