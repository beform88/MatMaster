from typing import AsyncGenerator, override

from google.adk.agents import InvocationContext, LlmAgent
from google.adk.events import Event

from agents.matmaster_agent.utils.event_utils import send_error_event


class ErrorHandleAgent(LlmAgent):
    @override
    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        try:
            # 修改这里：调用一个可重写的方法
            async for event in self._process_events(ctx):
                yield event
        except BaseException as err:
            async for error_event in send_error_event(err, ctx, self.name):
                yield error_event

    async def _process_events(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        """可重写的方法，专门处理事件循环"""
        async for event in super()._run_async_impl(ctx):
            yield event
