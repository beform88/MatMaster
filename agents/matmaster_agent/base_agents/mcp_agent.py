import json
import logging
from typing import Any, AsyncGenerator, Optional, cast

from google.adk.agents import InvocationContext
from google.adk.events import Event, EventActions
from pydantic import model_validator

from agents.matmaster_agent.base_agents.abc_agent import BaseMixin
from agents.matmaster_agent.base_agents.error_agent import ErrorHandleLlmAgent
from agents.matmaster_agent.base_callbacks.private_callback import (
    catch_after_tool_callback_error,
    catch_before_tool_callback_error,
    check_before_tool_callback_effect,
    check_job_create,
    check_user_phonon_balance,
    default_after_tool_callback,
    default_before_tool_callback,
    default_cost_func,
    inject_current_env,
    inject_userId_sessionId,
    inject_username_ticket,
    remove_job_link,
    tgz_oss_to_oss_list,
)
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
from agents.matmaster_agent.model import CostFuncType
from agents.matmaster_agent.utils.event_utils import (
    all_text_event,
    context_function_event,
    context_multipart2function_event,
    display_failed_result_or_consume,
    display_future_consume_event,
    is_function_call,
    is_function_response,
    is_text,
    update_state_event,
)
from agents.matmaster_agent.utils.frontend import get_frontend_job_result_data
from agents.matmaster_agent.utils.helper_func import load_tool_response, parse_result

logger = logging.getLogger(__name__)


class MCPInitMixin(BaseMixin):
    loading: bool = False  # Whether the agent display loading state
    render_tool_response: bool = False  # Whether render tool response in frontend
    enable_tgz_unpack: bool = True  # Whether unpack tgz files for tool_results
    cost_func: Optional[CostFuncType] = None


class MCPCallbackMixin(BaseMixin):
    @model_validator(mode='before')
    @classmethod
    def decorate_callbacks(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data

        if data.get('before_tool_callback') is None:
            data['before_tool_callback'] = default_before_tool_callback

        if data.get('after_tool_callback') is None:
            data['after_tool_callback'] = default_after_tool_callback

        if data.get('cost_func') is None:
            data['cost_func'] = default_cost_func

        if data.get('enable_tgz_unpack') is None:
            data['enable_tgz_unpack'] = True

        data['before_tool_callback'] = catch_before_tool_callback_error(
            inject_current_env(
                inject_username_ticket(
                    check_job_create(
                        check_user_phonon_balance(
                            inject_userId_sessionId(data['before_tool_callback']),
                            data['cost_func'],
                        )
                    )
                )
            )
        )

        data['after_tool_callback'] = check_before_tool_callback_effect(
            catch_after_tool_callback_error(
                remove_job_link(
                    tgz_oss_to_oss_list(
                        data['after_tool_callback'], data['enable_tgz_unpack']
                    )
                )
            )
        )

        return data


class MCPRunEventsMixin(BaseMixin):
    async def _run_events(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        parent = super()
        if hasattr(parent, '_run_events'):
            _run_events = cast(Any, parent)._run_events
            async for event in _run_events(ctx):
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
                    # update state: `tools_count`
                    yield update_state_event(
                        ctx,
                        state_delta={
                            'tools_count': ctx.session.state['tools_count'] + 1
                        },
                    )
                    # prompt user photon cost
                    cost_func = self.cost_func
                    async for future_consume_event in display_future_consume_event(
                        event, cost_func, ctx, self.name
                    ):
                        yield future_consume_event
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
                                    TMP_FRONTEND_STATE_KEY: {
                                        LOADING_STATE_KEY: LOADING_END
                                    }
                                }
                            ),
                        )

                    # Parse Tool Response
                    try:
                        dict_result = load_tool_response(event)
                        async for (
                            display_or_consume_event
                        ) in display_failed_result_or_consume(
                            dict_result, ctx, self.name, event
                        ):
                            yield display_or_consume_event
                    except BaseException:
                        yield event
                        raise

                    job_result = await parse_result(dict_result)
                    job_result_comp_data = get_frontend_job_result_data(job_result)

                    # 包装成function_call，来避免在历史记录中展示；同时模型可以在上下文中感知
                    for system_job_result_event in context_function_event(
                        ctx,
                        self.name,
                        'matmaster_job_result',
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
                            ctx, self.name, event, 'matmaster_sync_mcp_event'
                        ):
                            yield multi_part_event
                else:
                    yield event


class MCPAgent(MCPInitMixin, MCPCallbackMixin, ErrorHandleLlmAgent):
    pass
