import datetime
import logging
import time
from contextlib import contextmanager
from typing import AsyncGenerator

from google.adk.agents import InvocationContext, LlmAgent
from google.adk.agents.base_agent import BaseAgentState
from google.adk.events import Event
from google.adk.flows.llm_flows.base_llm_flow import BaseLlmFlow
from google.adk.flows.llm_flows.single_flow import SingleFlow
from google.adk.models import LlmRequest
from google.adk.utils.context_utils import Aclosing

from agents.matmaster_agent.constant import MATMASTER_AGENT_NAME

logger = logging.getLogger(__name__)


@contextmanager
def patch_run_async_impl():
    original_LlmAgent_run_async_impl = LlmAgent._run_async_impl
    original_SingleFlow_run_async = SingleFlow.run_async
    original_BaseLlmFlow_run_one_step_async = BaseLlmFlow._run_one_step_async

    async def patched_BaseLlmFlow_run_one_step_async(
        self,
        invocation_context: InvocationContext,
    ) -> AsyncGenerator[Event, None]:
        """One step means one LLM call."""
        logger.info(
            f'[{MATMASTER_AGENT_NAME}] [Timing] Patched patched_BaseLlmFlow_run_one_step_async Start {time.time()}'
        )
        logger.info(
            f'[{MATMASTER_AGENT_NAME}] [Timing] Patched patched_BaseLlmFlow_run_one_step_async before llm_request {time.time()}'
        )
        llm_request = LlmRequest()
        logger.info(
            f'[{MATMASTER_AGENT_NAME}] [Timing] Patched patched_BaseLlmFlow_run_one_step_async after llm_request {time.time()}'
        )

        logger.info(
            f'[{MATMASTER_AGENT_NAME}] [Timing] Patched patched_BaseLlmFlow_run_one_step_async before _preprocess_async {time.time()}'
        )
        # Preprocess before calling the LLM.
        async with Aclosing(
            self._preprocess_async(invocation_context, llm_request)
        ) as agen:
            async for event in agen:
                yield event
        if invocation_context.end_invocation:
            return
        logger.info(
            f'[{MATMASTER_AGENT_NAME}] [Timing] Patched patched_BaseLlmFlow_run_one_step_async after _preprocess_async {time.time()}'
        )

        logger.info(
            f'[{MATMASTER_AGENT_NAME}] [Timing] Patched patched_BaseLlmFlow_run_one_step_async before _get_events {time.time()}'
        )
        # Resume the LLM agent based on the last event from the current branch.
        # 1. User content: continue the normal flow
        # 2. Function call: call the tool and get the response event.
        events = invocation_context._get_events(
            current_invocation=True, current_branch=True
        )
        logger.info(
            f'[{MATMASTER_AGENT_NAME}] [Timing] Patched patched_BaseLlmFlow_run_one_step_async after _get_events {time.time()}'
        )
        if (
            invocation_context.is_resumable
            and events
            and events[-1].get_function_calls()
        ):
            model_response_event = events[-1]
            async with Aclosing(
                self._postprocess_handle_function_calls_async(
                    invocation_context, model_response_event, llm_request
                )
            ) as agen:
                async for event in agen:
                    event.id = Event.new_id()
                    yield event
                return

        logger.info(
            f'[{MATMASTER_AGENT_NAME}] [Timing] Patched patched_BaseLlmFlow_run_one_step_async before _call_llm_async {time.time()}'
        )
        # Calls the LLM.
        model_response_event = Event(
            id=Event.new_id(),
            invocation_id=invocation_context.invocation_id,
            author=invocation_context.agent.name,
            branch=invocation_context.branch,
        )
        async with Aclosing(
            self._call_llm_async(invocation_context, llm_request, model_response_event)
        ) as agen:
            logger.info(
                f'[{MATMASTER_AGENT_NAME}] [Timing] Patched patched_BaseLlmFlow_run_one_step_async before agen {time.time()}'
            )
            async for llm_response in agen:
                logger.info(
                    f'[{MATMASTER_AGENT_NAME}] [Timing] Patched patched_BaseLlmFlow_run_one_step_async before _postprocess_async {time.time()}'
                )
                # Postprocess after calling the LLM.
                async with Aclosing(
                    self._postprocess_async(
                        invocation_context,
                        llm_request,
                        llm_response,
                        model_response_event,
                    )
                ) as agen:
                    logger.info(
                        f'[{MATMASTER_AGENT_NAME}] [Timing] Patched patched_BaseLlmFlow_run_one_step_async before agen-for {time.time()}'
                    )
                    async for event in agen:
                        # Update the mutable event id to avoid conflict
                        model_response_event.id = Event.new_id()
                        model_response_event.timestamp = (
                            datetime.datetime.now().timestamp()
                        )
                        logger.info(
                            f'[{MATMASTER_AGENT_NAME}] [Timing] Patched patched_BaseLlmFlow_run_one_step_async before agen-event {time.time()}'
                        )
                        yield event
                        logger.info(
                            f'[{MATMASTER_AGENT_NAME}] [Timing] Patched patched_BaseLlmFlow_run_one_step_async after agen-event {time.time()}'
                        )
                    logger.info(
                        f'[{MATMASTER_AGENT_NAME}] [Timing] Patched patched_BaseLlmFlow_run_one_step_async after agen-for {time.time()}'
                    )
                logger.info(
                    f'[{MATMASTER_AGENT_NAME}] [Timing] Patched patched_BaseLlmFlow_run_one_step_async after _postprocess_async {time.time()}'
                )
            logger.info(
                f'[{MATMASTER_AGENT_NAME}] [Timing] Patched patched_BaseLlmFlow_run_one_step_async after agen {time.time()}'
            )
        logger.info(
            f'[{MATMASTER_AGENT_NAME}] [Timing] Patched patched_BaseLlmFlow_run_one_step_async after _call_llm_async {time.time()}'
        )

        logger.info(
            f'[{MATMASTER_AGENT_NAME}] [Timing] Patched patched_BaseLlmFlow_run_one_step_async End {time.time()}'
        )

    async def patched_SingleFlow_run_async(
        self, invocation_context: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        """Runs the flow."""
        logger.info(
            f'[{MATMASTER_AGENT_NAME}] [Timing] Patched Start patched_SingleFlow_run_async {time.time()}'
        )
        while True:
            last_event = None

            logger.info(
                f'[{MATMASTER_AGENT_NAME}] [Timing] Patched patched_SingleFlow_run_async before event {time.time()}'
            )

            BaseLlmFlow._run_one_step_async = patched_BaseLlmFlow_run_one_step_async
            try:
                async with Aclosing(
                    self._run_one_step_async(invocation_context)
                ) as agen:
                    async for event in agen:
                        last_event = event
                        yield event
            finally:
                BaseLlmFlow._run_one_step_async = (
                    original_BaseLlmFlow_run_one_step_async
                )

            logger.info(
                f'[{MATMASTER_AGENT_NAME}] [Timing] Patched patched_SingleFlow_run_async after event {time.time()}'
            )

            if not last_event or last_event.is_final_response() or last_event.partial:
                if last_event and last_event.partial:
                    logger.warning('The last event is partial, which is not expected.')
                break
        logger.info(
            f'[{MATMASTER_AGENT_NAME}] [Timing] Patched End patched_SingleFlow_run_async {time.time()}'
        )

    async def patched_method(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        logger.info(
            f'[{MATMASTER_AGENT_NAME}] [Timing] Patched Start _run_async_impl {time.time()}'
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

        logger.info(
            f'[{MATMASTER_AGENT_NAME}] [Timing] Patched _run_async_impl before _llm_flow {time.time()}'
        )

        SingleFlow.run_async = patched_SingleFlow_run_async
        try:
            async with Aclosing(self._llm_flow.run_async(ctx)) as agen:
                async for event in agen:
                    logger.info(
                        f'[{MATMASTER_AGENT_NAME}] [Timing] Patched _llm_flow before __maybe_save_output_to_state {time.time()}'
                    )
                    # 使用 _LlmAgent__maybe_save_output_to_state 来绕过名称修饰
                    if hasattr(self, '_LlmAgent__maybe_save_output_to_state'):
                        self._LlmAgent__maybe_save_output_to_state(event)
                    logger.info(
                        f'[{MATMASTER_AGENT_NAME}] [Timing] Patched _llm_flow after __maybe_save_output_to_state {time.time()}'
                    )
                    logger.info(
                        f'[{MATMASTER_AGENT_NAME}] [Timing] Patched _llm_flow before event {time.time()}'
                    )
                    yield event
                    logger.info(
                        f'[{MATMASTER_AGENT_NAME}] [Timing] Patched _llm_flow after event {time.time()}'
                    )
                    if ctx.should_pause_invocation(event):
                        return
            logger.info(
                f'[{MATMASTER_AGENT_NAME}] [Timing] Patched _run_async_impl after _llm_flow {time.time()}'
            )
        finally:
            SingleFlow.run_async = original_SingleFlow_run_async

        if ctx.is_resumable:
            yield self._create_agent_state_event(ctx, end_of_agent=True)

        logger.info(
            f'[{MATMASTER_AGENT_NAME}] [Timing] Patched End _run_async_impl {time.time()}'
        )

    LlmAgent._run_async_impl = patched_method

    try:
        yield
    finally:
        LlmAgent._run_async_impl = original_LlmAgent_run_async_impl
