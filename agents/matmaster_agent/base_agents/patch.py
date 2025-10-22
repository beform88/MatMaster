import logging
import time
from contextlib import contextmanager
from typing import AsyncGenerator

from google.adk.agents import InvocationContext, LlmAgent
from google.adk.agents.base_agent import BaseAgentState
from google.adk.events import Event
from google.adk.utils.context_utils import Aclosing

from agents.matmaster_agent.constant import MATMASTER_AGENT_NAME

logger = logging.getLogger(__name__)


@contextmanager
def patch_run_async_impl():
    original = LlmAgent._run_async_impl

    async def patched_method(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        logger.info(
            f'[{MATMASTER_AGENT_NAME}] [Timing] Patched _run_async_impl {time.time()}'
        )
        agent_state = self._load_agent_state(ctx, BaseAgentState)

        # If there is an sub-agent to resume, run it and then end the current
        # agent.
        if agent_state is not None and (
            agent_to_transfer := self._get_subagent_to_resume(ctx)
        ):
            async with Aclosing(agent_to_transfer.run_async(ctx)) as agen:
                async for event in agen:
                    yield event

            yield self._create_agent_state_event(ctx, end_of_agent=True)
            return

        async with Aclosing(self._llm_flow.run_async(ctx)) as agen:
            async for event in agen:
                # 使用 _LlmAgent__maybe_save_output_to_state 来绕过名称修饰
                if hasattr(self, '_LlmAgent__maybe_save_output_to_state'):
                    self._LlmAgent__maybe_save_output_to_state(event)
                yield event
                if ctx.should_pause_invocation(event):
                    return

        if ctx.is_resumable:
            yield self._create_agent_state_event(ctx, end_of_agent=True)

    LlmAgent._run_async_impl = patched_method

    try:
        yield
    finally:
        LlmAgent._run_async_impl = original
