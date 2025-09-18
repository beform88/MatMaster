import logging
import traceback
import uuid
from typing import Iterable
from typing import Optional

from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from google.genai.types import Content, FunctionCall, FunctionResponse, Part

from agents.matmaster_agent.constant import ModelRole
from agents.matmaster_agent.utils.helper_func import update_session_state

logger = logging.getLogger(__name__)


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
            not event.content.parts[0].text.startswith('<bohrium-chat-msg>')
    )


def is_function_call(event: Event) -> bool:
    """检查事件是否包含函数调用"""
    return has_part(event) and any(part.function_call for part in event.content.parts)


def get_function_call_indexes(event: Event):
    return [index for index, part in enumerate(event.content.parts) if part.function_call]


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
    function_call_id = f"added_{str(uuid.uuid4()).replace('-', '')[:24]}"
    yield context_function_call_event(ctx, author, function_call_id, function_call_name, role, args)
    yield context_function_response_event(ctx, author, function_call_id, function_call_name, response, role)


def context_multipart2function_event(ctx: InvocationContext, author: str, event: Event, function_call_name: str):
    for part in event.content.parts:
        if part.text:
            yield from context_function_event(ctx, author, function_call_name, {'msg': part.text},
                                              ModelRole)
        elif part.function_call:
            logger.warning(f"[context_multipart2function_event] function_name = {part.function_call.name}")
            yield context_function_call_event(ctx, author, function_call_id=part.function_call.id,
                                              function_call_name=part.function_call.name, role=ModelRole,
                                              args=part.function_call.args)


# 数据库 & 前端都感知
def all_text_event(ctx: InvocationContext, author: str, text: str, role: str):
    yield frontend_text_event(ctx, author, text, role)
    yield context_text_event(ctx, author, text, role)


def cherry_pick_events(ctx: InvocationContext):
    events = ctx.session.events
    cherry_pick_parts = []
    for event in events:
        if event.content:
            for part in event.content.parts:
                if part.text:
                    cherry_pick_parts.append((event.content.role, part.text))

    return cherry_pick_parts


async def send_error_event(err, ctx: InvocationContext, author):
    ctx.session.state['error_occurred'] = True
    await update_session_state(ctx, author)

    # 判断是否是异常组
    if isinstance(err, BaseExceptionGroup):
        error_details = [
            f"Exception Group caught with {len(err.exceptions)} exceptions:",
            f"Message: {str(err)}",
            '\nIndividual exceptions:'
        ]
        exceptions: Optional[Iterable[BaseException]] = err.exceptions
    else:
        error_details = [
            'Single Exception caught:',
            f"Type: {type(err).__name__}",
            f"Message: {str(err)}",
            '\nTraceback:',
            ''.join(traceback.format_tb(err.__traceback__))
        ]
        exceptions = None  # 单一异常时不再循环子异常

    # 如果是异常组，逐个子异常处理
    if exceptions:
        for i, exc in enumerate(exceptions, 1):
            error_details.append(f"\nException #{i}:")
            error_details.append(f"Type: {type(exc).__name__}")
            error_details.append(f"Message: {str(exc)}")
            error_details.append(f"Traceback: {''.join(traceback.format_tb(exc.__traceback__))}")

    # 合并错误信息
    detailed_error = '\n'.join(error_details)

    # 发送系统错误事件
    for event in context_function_event(ctx, author, 'system_detail_error',
                                        {'msg': detailed_error}, ModelRole):
        yield event
