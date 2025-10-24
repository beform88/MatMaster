import json
import logging
from typing import Any, AsyncGenerator, Optional, cast

from google.adk.agents import InvocationContext
from google.adk.events import Event, EventActions
from pydantic import Field

from agents.matmaster_agent.base_agents.error_agent import ErrorHandleAgent
from agents.matmaster_agent.base_callbacks.private_callback import (
    catch_after_tool_callback_error,
    catch_before_tool_callback_error,
    check_before_tool_callback_effect,
    check_job_create,
    check_user_phonon_balance,
    default_after_model_callback,
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


class MCPInitMixin:
    loading: bool = Field(
        False, description='Whether the agent display loading state', exclude=True
    )
    render_tool_response: bool = Field(
        False, description='Whether render tool response in frontend', exclude=True
    )
    enable_tgz_unpack: bool = Field(
        True, description='Whether unpack tgz files for tool_results'
    )
    cost_func: Optional[CostFuncType] = None

    def __init__(
        self,
        model,
        name,
        instruction='',
        description='',
        sub_agents=None,
        global_instruction='',
        tools=None,
        output_key=None,
        before_agent_callback=None,
        before_model_callback=None,
        before_tool_callback=default_before_tool_callback,
        after_tool_callback=default_after_tool_callback,
        after_model_callback=default_after_model_callback,
        after_agent_callback=None,
        disallow_transfer_to_parent=False,
        loading=False,
        render_tool_response=False,
        enable_tgz_unpack=True,
        cost_func=default_cost_func,
        **kwargs,
    ):
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
        before_tool_callback = catch_before_tool_callback_error(
            inject_current_env(
                inject_username_ticket(
                    check_job_create(
                        check_user_phonon_balance(
                            inject_userId_sessionId(before_tool_callback), cost_func
                        )
                    )
                )
            )
        )
        after_tool_callback = check_before_tool_callback_effect(
            catch_after_tool_callback_error(
                remove_job_link(
                    tgz_oss_to_oss_list(after_tool_callback, enable_tgz_unpack)
                )
            )
        )

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
            disallow_transfer_to_parent=disallow_transfer_to_parent,
            **kwargs,
        )

        self.loading = loading
        self.render_tool_response = render_tool_response
        self.enable_tgz_unpack = enable_tgz_unpack
        self.cost_func = cost_func


class MCPRunEventsMixin:
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
                    cost_func = self.parent_agent.cost_func
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


class MCPFeaturesMixin(MCPInitMixin, MCPRunEventsMixin):
    pass


class MCPInitAgentComp(MCPInitMixin, ErrorHandleAgent):
    pass


class MCPAgentComp(MCPFeaturesMixin, ErrorHandleAgent):
    def __init__(
        self,
        *args,
        loading=False,
        enable_tgz_unpack=True,
        cost_func=None,
        render_tool_response=False,
        **kwargs,
    ):
        # 先执行 MCPFeaturesMixin 的 init，遇到 super 的时候再执行 ErrorHandleAgent 的 init
        super().__init__(
            *args,
            loading=loading,
            enable_tgz_unpack=enable_tgz_unpack,
            cost_func=cost_func,
            render_tool_response=render_tool_response,
            **kwargs,
        )
