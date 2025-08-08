import asyncio
import base64
import json
import logging
import os
import shutil
import tarfile
import time
import traceback
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import aiofiles
import aiohttp
import oss2
import requests
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event, EventActions
from google.genai.types import Content, FunctionCall, FunctionResponse, Part
from oss2.credentials import EnvironmentVariableCredentialsProvider

from agents.matmaster_agent.constant import ModelRole, OPENAPI_HOST, BOHRIUM_API_URL
from agents.matmaster_agent.model import JobResult, JobResultType


# event check funcs
def has_part(event: Event):
    return (
            event and
            event.content and
            event.content.parts and
            len(event.content.parts) and
            event.content.parts[0]
    )


def is_text(event: Event):
    return (
            has_part(event) and
            event.content.parts[0].text
    )


def is_text_and_not_bohrium(event: Event):
    return (
            is_text(event) and
            not event.content.parts[0].text.startswith("<bohrium-chat-msg>")
    )


def is_function_call(event: Event):
    return (
            has_part(event) and
            event.content.parts[0].function_call
    )


def is_function_response(event: Event):
    return (
            has_part(event) and
            event.content.parts[0].function_response
    )


# event send funcs
# 仅前端感知
def frontend_text_event(ctx: InvocationContext, author: str, text: str, role: str):
    return Event(
        author=author,
        branch=ctx.branch,
        invocation_id=ctx.invocation_id,
        content=Content(parts=[Part(text=text)], role=role),
        partial=True)


def frontend_function_call_event(ctx: InvocationContext, author: str, function_call: FunctionCall, role: str):
    return Event(
        author=author,
        invocation_id=ctx.invocation_id,
        content=Content(
            parts=[Part(function_call=FunctionCall(
                id=f"frontend_{function_call.name}",
                name=function_call.name,
                args=function_call.args
            ))],
            role=role,
        ),
        partial=True
    )


def frontend_function_response_event(ctx: InvocationContext, author: str, function_call: FunctionCall, role: str):
    return Event(
        author=author,
        invocation_id=ctx.invocation_id,
        content=Content(
            parts=[Part(function_response=FunctionResponse(
                id=f"frontend_{function_call.name}",
                name=function_call.name,
                response=None
            ))],
            role=role,
        ),
        partial=True
    )


# 仅模型上下文感知
def context_text_event(ctx: InvocationContext, author: str, text: str, role: str):
    return Event(
        author=author,
        branch=ctx.branch,
        invocation_id=ctx.invocation_id,
        content=Content(parts=[Part(text=text)], role=role),
        partial=False)


def context_function_call_event(ctx: InvocationContext, author: str, function_call_id: str, function_call_name: str,
                                role: str, args: Optional[dict] = None):
    return Event(
        author=author,
        invocation_id=ctx.invocation_id,
        content=Content(
            parts=[Part(function_call=FunctionCall(
                id=function_call_id,
                name=function_call_name,
                args=args,
            ))],
            role=role,
        ),
        partial=False
    )


def context_function_response_event(ctx: InvocationContext, author: str, function_call_id: str, function_call_name: str,
                                    response: Optional[dict], role: str):
    return Event(
        author=author,
        invocation_id=ctx.invocation_id,
        content=Content(
            parts=[Part(function_response=FunctionResponse(
                id=function_call_id,
                name=function_call_name,
                response=response
            ))],
            role=role,
        ),
        partial=False
    )


def context_function_event(ctx: InvocationContext, author: str, function_call_name: str, response: Optional[dict],
                           role: str, args: Optional[dict] = None):
    function_call_id = f"call_{str(uuid.uuid4()).replace('-', '')[:24]}"
    yield context_function_call_event(ctx, author, function_call_id, function_call_name, role, args)
    yield context_function_response_event(ctx, author, function_call_id, function_call_name, response, role)


# 数据库 & 前端都感知
def all_text_event(ctx: InvocationContext, author: str, text: str, role: str):
    yield frontend_text_event(ctx, author, text, role)
    yield context_text_event(ctx, author, text, role)


async def send_error_event(err, ctx, author, error_handle_agent=None):
    if not error_handle_agent:
        error_handle_agent = ctx.agent.parent_agent

    # 构建更详细的错误信息
    error_details = [
        f"Exception Group caught with {len(err.exceptions)} exceptions:",
        f"Message: {str(err)}",
        "\nIndividual exceptions:"
    ]

    # 添加每个子异常的详细信息
    for i, exc in enumerate(err.exceptions, 1):
        error_details.append(f"\nException #{i}:")
        error_details.append(f"Type: {type(exc).__name__}")
        error_details.append(f"Message: {str(exc)}")
        error_details.append(f"Traceback: {''.join(traceback.format_tb(exc.__traceback__))}")

    # 将所有信息合并为一个字符串
    detailed_error = "\n".join(error_details)
    # 包装成function_call，来避免在历史记录中展示；同时模型可以在上下文中感知
    for event in context_function_event(ctx, author, "system_detail_error",
                                        {"msg": detailed_error}, ModelRole):
        yield event

    async for error_event in error_handle_agent.run_async(ctx):
        yield error_event
