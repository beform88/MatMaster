import copy
import json
import logging
import os
import traceback
from functools import wraps
from typing import Optional, Union

import aiohttp
from dp.agent.adapter.adk import CalculationMCPTool
from google.adk.agents.callback_context import CallbackContext
from google.adk.agents.invocation_context import InvocationContext
from google.adk.agents.llm_agent import AfterToolCallback, BeforeToolCallback
from google.adk.models import LlmResponse
from google.adk.tools import BaseTool, ToolContext
from mcp.types import CallToolResult

from agents.matmaster_agent.constant import (
    CURRENT_ENV,
    FRONTEND_STATE_KEY,
    OPENAPI_HOST,
    Transfer2Agent,
)
from agents.matmaster_agent.utils.auth import ak_to_username, ak_to_ticket
from agents.matmaster_agent.utils.helper_func import is_json, get_same_function_call
from agents.matmaster_agent.utils.io_oss import extract_convert_and_upload

logger = logging.getLogger(__name__)


# after_model_callback
async def default_after_model_callback(callback_context: CallbackContext,
                                       llm_response: LlmResponse) -> Optional[LlmResponse]:
    # 检查响应是否有效
    if not (llm_response and llm_response.content and llm_response.content.parts and len(llm_response.content.parts)):
        return None

    # 获取所有函数调用
    current_function_calls = [part.function_call for part in llm_response.content.parts if part.function_call]

    # 如果没有函数调用，直接返回
    if not current_function_calls:
        return None

    # 处理多个函数调用的情况
    if len(current_function_calls) > 1:
        logger.info("Count of Function Calls > 1, check name & args now")
        repeat_indexes = get_same_function_call(current_function_calls)

        if repeat_indexes is not None:
            logger.info("Same Function Calls Detected, Remove Now")
            # 创建不包含重复索引的新部分列表
            llm_response.content.parts = [part for index, part in enumerate(copy.deepcopy(llm_response.content.parts))
                                          if index not in repeat_indexes]
            return llm_response

    return None


# before_tool_callback
async def default_before_tool_callback(tool, args, tool_context):
    return


def _get_session_state(ctx: Union[InvocationContext, ToolContext]):
    return ctx.session.state if isinstance(ctx, InvocationContext) else ctx.state


def _get_ak(ctx: Union[InvocationContext, ToolContext]):
    session_state = _get_session_state(ctx)
    return session_state[FRONTEND_STATE_KEY]['biz'].get('ak') or os.getenv("BOHRIUM_ACCESS_KEY")


def _get_projectId(ctx: Union[InvocationContext, ToolContext]):
    session_state = _get_session_state(ctx)
    return session_state[FRONTEND_STATE_KEY]['biz'].get('projectId') or os.getenv("BOHRIUM_PROJECT_ID")


def _inject_ak(ctx: Union[InvocationContext, ToolContext], executor, storage):
    access_key = _get_ak(ctx)
    if access_key is not None:
        if executor is not None:
            if executor['type'] == "dispatcher":  # BohriumExecutor
                executor['machine']['remote_profile']['access_key'] = access_key
            elif executor["type"] == "local" and executor.get("dflow", False):  # DFlowExecutor
                executor['env']['BOHRIUM_ACCESS_KEY'] = access_key
        if storage is not None:  # BohriumStorage
            storage['plugin']['access_key'] = access_key
    return access_key, executor, storage


def _inject_projectId(ctx: Union[InvocationContext, ToolContext], executor, storage):
    project_id = _get_projectId(ctx)
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


def _inject_username(ctx: Union[InvocationContext, ToolContext], executor):
    access_key = _get_ak(ctx)
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
    else:
        raise RuntimeError("Failed to get username")


def _inject_ticket(ctx: Union[InvocationContext, ToolContext], executor):
    access_key = _get_ak(ctx)
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
    else:
        raise RuntimeError("Failed to get ticket")


def _inject_current_env(executor):
    if executor is not None:
        if executor['type'] == "dispatcher":  # BohriumExecutor
            # Redundant set for resources/envs keys
            executor["resources"] = executor.get("resources", {})
            executor["resources"]["envs"] = executor["resources"].get("envs", {})
            executor['resources']['envs']['CURRENT_ENV'] = str(CURRENT_ENV)
        elif executor["type"] == "local" and executor.get("dflow", False):  # DFlowExecutor
            executor['env']['CURRENT_ENV'] = str(CURRENT_ENV)
    return executor


def inject_ak_projectId(func: BeforeToolCallback) -> BeforeToolCallback:
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
            raise TypeError("Not CalculationMCPTool type, current tool does not have <storage>")

        # 获取 access_key
        access_key, tool.executor, tool.storage = _inject_ak(tool_context, tool.executor, tool.storage)
        if access_key is None:
            raise ValueError("Failed to get access_key")

        # 获取 project_id
        try:
            project_id, tool.executor, tool.storage = _inject_projectId(tool_context, tool.executor, tool.storage)
        except ValueError as e:
            raise ValueError("ProjectId is invalid") from e
        if project_id is None:
            raise RuntimeError("ProjectId was not provided. Please select the project first.")

        tool_context.state['ak'] = access_key
        tool_context.state['project_id'] = project_id

    return wrapper


def inject_username_ticket(func: BeforeToolCallback) -> BeforeToolCallback:
    @wraps(func)
    async def wrapper(tool: BaseTool, args: dict, tool_context: ToolContext) -> Optional[dict]:
        # 先执行前面的回调链
        if (before_tool_result := await func(tool, args, tool_context)) is not None:
            return before_tool_result

        # 注入 username
        _, tool.executor = _inject_username(tool_context, tool.executor)

        # 注入 ticket
        _, tool.executor = _inject_ticket(tool_context, tool.executor)

    return wrapper


def inject_current_env(func: BeforeToolCallback) -> BeforeToolCallback:
    @wraps(func)
    async def wrapper(tool: BaseTool, args: dict, tool_context: ToolContext) -> Optional[dict]:
        # 先执行前面的回调链
        if (before_tool_result := await func(tool, args, tool_context)) is not None:
            return before_tool_result

        # 注入当前环境
        tool.executor = _inject_current_env(tool.executor)

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
            raise TypeError("Not CalculationMCPTool type, current tool can't create job!")

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


# 总应该在最后
def catch_before_tool_callback_error(func: BeforeToolCallback) -> BeforeToolCallback:
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
                "traceback": traceback.format_exc()
            }

    return wrapper


# after_tool_callback
async def default_after_tool_callback(tool, args, tool_context, tool_response):
    return


def tgz_oss_to_oss_list(func: AfterToolCallback) -> AfterToolCallback:
    """Decorator that processes tool responses containing tgz files from OSS.

    This decorator performs the following operations:
    1. Calls the original after-tool callback function
    2. If the original callback returns a result, uses that result
    3. For CalculationMCPTool responses containing tgz file URLs:
       - Extracts the tgz files
       - Converts the contents
       - Uploads the processed files back to OSS
       - Returns a new result with updated file URLs

    Args:
        func: The after-tool callback function to be decorated

    Returns:
        A wrapper function that processes the tool response

    Raises:
        TypeError: If the tool is not of type CalculationMCPTool

    Example:
        The decorator processes responses containing tgz file URLs like:
        {
            "result1": "https://example.com/file1.tgz",
            "result2": "normal_value"
        }
        And converts them to:
        {
            "result1": "https://example.com/file1.tgz",
            "result2": "normal_value"
            “file1_part1”: "https://new-url/file1_part1",
            "file1_part1": "https://new-url/file1_part2",
        }
    """

    @wraps(func)
    async def wrapper(tool: BaseTool, args: dict, tool_context: ToolContext,
                      tool_response: Union[dict, CallToolResult]) -> Optional[dict]:
        # 两步操作：
        # 1. 调用被装饰的 before_tool_callback；
        # 2. 如果调用的 before_tool_callback 有返回值，以这个为准
        if (after_tool_result := await func(tool, args, tool_context, tool_response)) is not None:
            return after_tool_result

        # 如果 tool 不是 CalculationMCPTool，不应该调用这个 callback
        if not isinstance(tool, CalculationMCPTool):
            raise TypeError("Not CalculationMCPTool type")

        # 检查是否为有效的 json 字典
        if not (tool_response and
                tool_response.content and
                tool_response.content[0].text and
                is_json(tool_response.content[0].text)):
            return None

        tool_results = json.loads(tool_response.content[0].text)

        new_tool_result = {}
        tgz_flag = False
        for k, v in tool_results.items():
            new_tool_result[k] = v
            if (
                    type(v) == str and
                    v.startswith("https") and
                    v.endswith("tgz")):
                tgz_flag = True
                new_tool_result.update(**await extract_convert_and_upload(v))

        if tgz_flag:
            return new_tool_result

    return wrapper


def catch_after_tool_callback_error(func: AfterToolCallback) -> AfterToolCallback:
    @wraps(func)
    async def wrapper(tool: BaseTool, args: dict, tool_context: ToolContext,
                      tool_response: Union[dict, CallToolResult]) -> Optional[dict]:
        # 两步操作：
        # 1. 调用被装饰的 after_tool_callback；
        # 2. 如果调用的 after_tool_callback 有返回值，以这个为准
        try:
            if (after_tool_result := await func(tool, args, tool_context, tool_response)) is not None:
                return after_tool_result
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "error_type": type(e).__name__,
                "traceback": traceback.format_exc()
            }

    return wrapper


# 总应该在最后
def check_before_tool_callback_effect(func: AfterToolCallback) -> AfterToolCallback:
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
        # if `before_tool_callback` return dict
        if type(tool_response) is dict:
            return

        return await func(tool, args, tool_context, tool_response)

    return wrapper
