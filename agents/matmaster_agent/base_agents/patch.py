import datetime
import inspect
import logging
import time
from contextlib import contextmanager
from typing import AsyncGenerator, Optional

from google.adk.agents import InvocationContext, LiveRequestQueue, LlmAgent
from google.adk.agents.base_agent import BaseAgentState
from google.adk.agents.callback_context import CallbackContext
from google.adk.agents.readonly_context import ReadonlyContext
from google.adk.agents.run_config import StreamingMode
from google.adk.events import Event
from google.adk.flows.llm_flows.base_llm_flow import (
    _ADK_AGENT_NAME_LABEL_KEY,
    BaseLlmFlow,
)
from google.adk.flows.llm_flows.single_flow import SingleFlow
from google.adk.models import LlmRequest, LlmResponse
from google.adk.telemetry import trace_call_llm, tracer
from google.adk.utils.context_utils import Aclosing
from google.genai import types

from agents.matmaster_agent.constant import MATMASTER_AGENT_NAME

logger = logging.getLogger(__name__)


@contextmanager
def patch_run_async_impl():
    original_LlmAgent_run_async_impl = LlmAgent._run_async_impl
    original_SingleFlow_run_async = SingleFlow.run_async
    original_BaseLlmFlow_run_one_step_async = BaseLlmFlow._run_one_step_async
    original_BaseLlmFlow_call_llm_async = BaseLlmFlow._call_llm_async
    original_BaseLlmFlow_handle_after_model_callback = (
        BaseLlmFlow._handle_after_model_callback
    )

    async def patched_BaseLlmFlow_handle_after_model_callback(
        self,
        invocation_context: InvocationContext,
        llm_response: LlmResponse,
        model_response_event: Event,
    ) -> Optional[LlmResponse]:
        agent = invocation_context.agent

        # Add grounding metadata to the response if needed.
        # TODO(b/448114567): Remove this function once the workaround is no longer needed.
        async def _maybe_add_grounding_metadata(
            response: Optional[LlmResponse] = None,
        ) -> Optional[LlmResponse]:
            logger.info(
                f'[{MATMASTER_AGENT_NAME}] [Timing] Patched patched_BaseLlmFlow_handle_after_model_callback _maybe_add_grounding_metadata Start {time.time()}'
            )
            logger.info(
                f'[{MATMASTER_AGENT_NAME}] [Timing] Patched patched_BaseLlmFlow_handle_after_model_callback _maybe_add_grounding_metadata before readonly_context {time.time()}'
            )
            readonly_context = ReadonlyContext(invocation_context)
            logger.info(
                f'[{MATMASTER_AGENT_NAME}] [Timing] Patched patched_BaseLlmFlow_handle_after_model_callback _maybe_add_grounding_metadata after readonly_context {time.time()}'
            )
            logger.info(
                f'[{MATMASTER_AGENT_NAME}] [Timing] Patched patched_BaseLlmFlow_handle_after_model_callback _maybe_add_grounding_metadata before canonical_tools {time.time()}'
            )
            tools = await agent.canonical_tools(readonly_context)
            logger.info(
                f'[{MATMASTER_AGENT_NAME}] [Timing] Patched patched_BaseLlmFlow_handle_after_model_callback _maybe_add_grounding_metadata after canonical_tools {time.time()}'
            )
            if not any(tool.name == 'google_search_agent' for tool in tools):
                return response
            ground_metadata = invocation_context.session.state.get(
                'temp:_adk_grounding_metadata', None
            )
            if not ground_metadata:
                return response

            if not response:
                response = llm_response
            response.grounding_metadata = ground_metadata
            logger.info(
                f'[{MATMASTER_AGENT_NAME}] [Timing] Patched patched_BaseLlmFlow_handle_after_model_callback _maybe_add_grounding_metadata End {time.time()}'
            )
            return response

        callback_context = CallbackContext(
            invocation_context, event_actions=model_response_event.actions
        )

        logger.info(
            f'[{MATMASTER_AGENT_NAME}] [Timing] Patched patched_BaseLlmFlow_handle_after_model_callback before run_after_model_callback {time.time()}'
        )
        # First run callbacks from the plugins.
        callback_response = (
            await invocation_context.plugin_manager.run_after_model_callback(
                callback_context=CallbackContext(invocation_context),
                llm_response=llm_response,
            )
        )
        if callback_response:
            return await _maybe_add_grounding_metadata(callback_response)
        logger.info(
            f'[{MATMASTER_AGENT_NAME}] [Timing] Patched patched_BaseLlmFlow_handle_after_model_callback after run_after_model_callback {time.time()}'
        )

        # If no overrides are provided from the plugins, further run the canonical
        # callbacks.
        if not agent.canonical_after_model_callbacks:
            return await _maybe_add_grounding_metadata()
        for callback in agent.canonical_after_model_callbacks:
            logger.info(
                f'[{MATMASTER_AGENT_NAME}] [Timing] Patched patched_BaseLlmFlow_handle_after_model_callback before callback {time.time()}'
            )
            callback_response = callback(
                callback_context=callback_context, llm_response=llm_response
            )
            logger.info(
                f'[{MATMASTER_AGENT_NAME}] [Timing] Patched patched_BaseLlmFlow_handle_after_model_callback after callback {time.time()}'
            )
            logger.info(
                f'[{MATMASTER_AGENT_NAME}] [Timing] Patched patched_BaseLlmFlow_handle_after_model_callback before await callback {time.time()}'
            )
            if inspect.isawaitable(callback_response):
                callback_response = await callback_response
            logger.info(
                f'[{MATMASTER_AGENT_NAME}] [Timing] Patched patched_BaseLlmFlow_handle_after_model_callback after await callback {time.time()}'
            )
            logger.info(
                f'[{MATMASTER_AGENT_NAME}] [Timing] Patched patched_BaseLlmFlow_handle_after_model_callback before _maybe_add_grounding_metadata {time.time()}'
            )
            if callback_response:
                return await _maybe_add_grounding_metadata(callback_response)
            logger.info(
                f'[{MATMASTER_AGENT_NAME}] [Timing] Patched patched_BaseLlmFlow_handle_after_model_callback after _maybe_add_grounding_metadata {time.time()}'
            )
        return await _maybe_add_grounding_metadata()

    async def patched_BaseLlmFlow_call_llm_async(
        self,
        invocation_context: InvocationContext,
        llm_request: LlmRequest,
        model_response_event: Event,
    ) -> AsyncGenerator[LlmResponse, None]:
        logger.info(
            f'[{MATMASTER_AGENT_NAME}] [Timing] Patched patched_BaseLlmFlow_call_llm_async Start {time.time()}'
        )
        # Runs before_model_callback if it exists.
        if response := await self._handle_before_model_callback(
            invocation_context, llm_request, model_response_event
        ):
            yield response
            return

        llm_request.config = llm_request.config or types.GenerateContentConfig()
        llm_request.config.labels = llm_request.config.labels or {}

        # Add agent name as a label to the llm_request. This will help with slicing
        # the billing reports on a per-agent basis.
        if _ADK_AGENT_NAME_LABEL_KEY not in llm_request.config.labels:
            llm_request.config.labels[_ADK_AGENT_NAME_LABEL_KEY] = (
                invocation_context.agent.name
            )

        # Calls the LLM.
        if hasattr(self, '_BaseLlmFlow__get_llm'):
            llm = self._BaseLlmFlow__get_llm(invocation_context)

        async def _call_llm_with_tracing() -> AsyncGenerator[LlmResponse, None]:
            with tracer.start_as_current_span('call_llm'):
                if invocation_context.run_config.support_cfc:
                    invocation_context.live_request_queue = LiveRequestQueue()
                    responses_generator = self.run_live(invocation_context)
                    async with Aclosing(
                        self._run_and_handle_error(
                            responses_generator,
                            invocation_context,
                            llm_request,
                            model_response_event,
                        )
                    ) as agen:
                        async for llm_response in agen:
                            # Runs after_model_callback if it exists.
                            if altered_llm_response := await self._handle_after_model_callback(
                                invocation_context, llm_response, model_response_event
                            ):
                                llm_response = altered_llm_response
                            # only yield partial response in SSE streaming mode
                            if (
                                invocation_context.run_config.streaming_mode
                                == StreamingMode.SSE
                                or not llm_response.partial
                            ):
                                yield llm_response
                            if llm_response.turn_complete:
                                invocation_context.live_request_queue.close()
                else:
                    # Check if we can make this llm call or not. If the current call
                    # pushes the counter beyond the max set value, then the execution is
                    # stopped right here, and exception is thrown.
                    invocation_context.increment_llm_call_count()
                    responses_generator = llm.generate_content_async(
                        llm_request,
                        stream=invocation_context.run_config.streaming_mode
                        == StreamingMode.SSE,
                    )
                    logger.info(
                        f'[{MATMASTER_AGENT_NAME}] [Timing] Patched patched_BaseLlmFlow_call_llm_async before _run_and_handle_error {time.time()}'
                    )
                    async with Aclosing(
                        self._run_and_handle_error(
                            responses_generator,
                            invocation_context,
                            llm_request,
                            model_response_event,
                        )
                    ) as agen:
                        logger.info(
                            f'[{MATMASTER_AGENT_NAME}] [Timing] Patched patched_BaseLlmFlow_call_llm_async before _run_and_handle_error agen {time.time()}'
                        )
                        async for llm_response in agen:
                            logger.info(
                                f'[{MATMASTER_AGENT_NAME}] [Timing] Patched patched_BaseLlmFlow_call_llm_async before trace_call_llm {time.time()}'
                            )
                            trace_call_llm(
                                invocation_context,
                                model_response_event.id,
                                llm_request,
                                llm_response,
                            )
                            logger.info(
                                f'[{MATMASTER_AGENT_NAME}] [Timing] Patched patched_BaseLlmFlow_call_llm_async after trace_call_llm {time.time()}'
                            )
                            logger.info(
                                f'[{MATMASTER_AGENT_NAME}] [Timing] Patched patched_BaseLlmFlow_call_llm_async before _handle_after_model_callback {time.time()}'
                            )

                            logger.info(
                                f'[{MATMASTER_AGENT_NAME}] [Timing] Patched patched_BaseLlmFlow_call_llm_async before _handle_after_model_callback llm_response = {llm_response.model_dump_json()}'
                            )
                            BaseLlmFlow._handle_after_model_callback = (
                                patched_BaseLlmFlow_handle_after_model_callback
                            )
                            try:
                                # Runs after_model_callback if it exists.
                                if altered_llm_response := await self._handle_after_model_callback(
                                    invocation_context,
                                    llm_response,
                                    model_response_event,
                                ):
                                    llm_response = altered_llm_response
                            finally:
                                BaseLlmFlow._handle_after_model_callback = (
                                    original_BaseLlmFlow_handle_after_model_callback
                                )
                            logger.info(
                                f'[{MATMASTER_AGENT_NAME}] [Timing] Patched patched_BaseLlmFlow_call_llm_async after _handle_after_model_callback {time.time()}'
                            )

                            yield llm_response
                        logger.info(
                            f'[{MATMASTER_AGENT_NAME}] [Timing] Patched patched_BaseLlmFlow_call_llm_async after _run_and_handle_error agen {time.time()}'
                        )
                    logger.info(
                        f'[{MATMASTER_AGENT_NAME}] [Timing] Patched patched_BaseLlmFlow_call_llm_async after _run_and_handle_error {time.time()}'
                    )

        logger.info(
            f'[{MATMASTER_AGENT_NAME}] [Timing] Patched patched_BaseLlmFlow_call_llm_async before _call_llm_with_tracing {time.time()}'
        )
        async with Aclosing(_call_llm_with_tracing()) as agen:
            logger.info(
                f'[{MATMASTER_AGENT_NAME}] [Timing] Patched patched_BaseLlmFlow_call_llm_async before agen-for {time.time()}'
            )
            async for event in agen:
                logger.info(
                    f'[{MATMASTER_AGENT_NAME}] [Timing] Patched patched_BaseLlmFlow_call_llm_async before agen-event {time.time()}'
                )
                yield event
                logger.info(
                    f'[{MATMASTER_AGENT_NAME}] [Timing] Patched patched_BaseLlmFlow_call_llm_async after agen-event {time.time()}'
                )
            logger.info(
                f'[{MATMASTER_AGENT_NAME}] [Timing] Patched patched_BaseLlmFlow_call_llm_async after agen-for {time.time()}'
            )
        logger.info(
            f'[{MATMASTER_AGENT_NAME}] [Timing] Patched patched_BaseLlmFlow_call_llm_async after _call_llm_with_tracing {time.time()}'
        )

        logger.info(
            f'[{MATMASTER_AGENT_NAME}] [Timing] Patched patched_BaseLlmFlow_call_llm_async End {time.time()}'
        )

    async def patched_BaseLlmFlow_run_one_step_async(
        self,
        invocation_context: InvocationContext,
    ) -> AsyncGenerator[Event, None]:
        """One step means one LLM call."""
        logger.info(
            f'[{MATMASTER_AGENT_NAME}] [Timing] Patched patched_BaseLlmFlow_run_one_step_async Start {time.time()}'
        )
        llm_request = LlmRequest()

        # Preprocess before calling the LLM.
        async with Aclosing(
            self._preprocess_async(invocation_context, llm_request)
        ) as agen:
            async for event in agen:
                yield event
        if invocation_context.end_invocation:
            return

        # Resume the LLM agent based on the last event from the current branch.
        # 1. User content: continue the normal flow
        # 2. Function call: call the tool and get the response event.
        events = invocation_context._get_events(
            current_invocation=True, current_branch=True
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

        # Calls the LLM.
        model_response_event = Event(
            id=Event.new_id(),
            invocation_id=invocation_context.invocation_id,
            author=invocation_context.agent.name,
            branch=invocation_context.branch,
        )

        BaseLlmFlow._call_llm_async = patched_BaseLlmFlow_call_llm_async
        try:
            logger.info(
                f'[{MATMASTER_AGENT_NAME}] [Timing] Patched patched_BaseLlmFlow_run_one_step_async before _call_llm_async {time.time()}'
            )
            async with Aclosing(
                self._call_llm_async(
                    invocation_context, llm_request, model_response_event
                )
            ) as agen:
                logger.info(
                    f'[{MATMASTER_AGENT_NAME}] [Timing] Patched patched_BaseLlmFlow_run_one_step_async before agen {time.time()}'
                )
                # +3s
                async for llm_response in agen:  # time cost
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
                        async for event in agen:
                            # Update the mutable event id to avoid conflict
                            model_response_event.id = Event.new_id()
                            model_response_event.timestamp = (
                                datetime.datetime.now().timestamp()
                            )
                            yield event
                    logger.info(
                        f'[{MATMASTER_AGENT_NAME}] [Timing] Patched patched_BaseLlmFlow_run_one_step_async after _postprocess_async {time.time()}'
                    )
                logger.info(
                    f'[{MATMASTER_AGENT_NAME}] [Timing] Patched patched_BaseLlmFlow_run_one_step_async after agen {time.time()}'
                )
        finally:
            BaseLlmFlow._call_llm_async = original_BaseLlmFlow_call_llm_async
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
