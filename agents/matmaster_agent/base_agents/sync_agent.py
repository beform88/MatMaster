import json
import logging
from typing import AsyncGenerator, override

from google.adk.agents import InvocationContext
from google.adk.events import Event, EventActions

from agents.matmaster_agent.base_agents.mcp_agent import MCPLlmAgent
from agents.matmaster_agent.constant import (
    JOB_RESULT_KEY,
    LOADING_DESC,
    LOADING_END,
    LOADING_START,
    LOADING_STATE_KEY,
    LOADING_TITLE,
    TMP_FRONTEND_STATE_KEY,
    ModelRole,
)
from agents.matmaster_agent.utils.event_utils import (
    all_text_event,
    context_function_event,
    context_multipart2function_event,
    is_function_call,
    is_function_response,
    is_text,
    photon_consume_event,
)
from agents.matmaster_agent.utils.frontend import get_frontend_job_result_data
from agents.matmaster_agent.utils.helper_func import load_tool_response, parse_result

logger = logging.getLogger(__name__)


# LlmAgent -> ErrorHandleAgent -> SubordinateAgent -> MCPLlmAgent -> SyncMCPLlmAgent
class SyncMCPLlmAgent(MCPLlmAgent):
    # Execution Order: user_question -> chembrain_llm -> event -> user_agree_transfer -> retrosyn_llm (param) -> event
    #                  -> user_agree_param -> retrosyn_llm (function_call) -> event -> tool_call
    #                  -> retrosyn_llm (function_response) -> event
    @override
    async def _run_events(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        async for event in super()._run_events(ctx):
            if is_function_call(event):
                if self.loading:
                    loading_title_msg = (
                        f"正在调用 {event.content.parts[0].function_call.name}..."
                    )
                    loading_desc_msg = '结果生成中，请稍等片刻...'
                    logger.info(loading_title_msg)
                    yield Event(
                        author=self.name,
                        actions=EventActions(
                            state_delta={
                                TMP_FRONTEND_STATE_KEY: {
                                    LOADING_STATE_KEY: LOADING_START,
                                    LOADING_TITLE: loading_title_msg,
                                    LOADING_DESC: loading_desc_msg,
                                }
                            }
                        ),
                    )
            elif is_function_response(event):
                # Loading Event
                if self.loading:
                    logger.info(
                        f"{event.content.parts[0].function_response.name} 调用结束"
                    )
                    yield Event(
                        author=self.name,
                        actions=EventActions(
                            state_delta={
                                TMP_FRONTEND_STATE_KEY: {LOADING_STATE_KEY: LOADING_END}
                            }
                        ),
                    )

                # Parse Tool Response
                try:
                    dict_result = load_tool_response(event)
                    async for consume_event in photon_consume_event(
                        ctx, event, self.name
                    ):
                        yield consume_event
                except BaseException:
                    yield event
                    raise

                job_result = await parse_result(dict_result)
                job_result_comp_data = get_frontend_job_result_data(job_result)

                # 包装成function_call，来避免在历史记录中展示；同时模型可以在上下文中感知
                for system_job_result_event in context_function_event(
                    ctx,
                    self.name,
                    'system_job_result',
                    {JOB_RESULT_KEY: job_result},
                    ModelRole,
                ):
                    yield system_job_result_event

                # Render Tool Response Event
                if self.render_tool_response:
                    for result_event in all_text_event(
                        ctx,
                        self.name,
                        f"<bohrium-chat-msg>{json.dumps(job_result_comp_data)}</bohrium-chat-msg>",
                        ModelRole,
                    ):
                        yield result_event

            if is_text(event):
                if not event.partial:
                    for multi_part_event in context_multipart2function_event(
                        ctx, self.name, event, 'system_sync_mcp_agent'
                    ):
                        yield multi_part_event
            else:
                yield event
