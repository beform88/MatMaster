import logging
from typing import AsyncGenerator, override

from google.adk.agents import InvocationContext, LlmAgent
from google.adk.events import Event

from agents.matmaster_agent.constant import (
    MATMASTER_AGENT_NAME,
    ModelRole,
)
from agents.matmaster_agent.utils.event_utils import (
    context_function_event,
    update_state_event,
)

logger = logging.getLogger(__name__)


class ToolValidatorAgent(LlmAgent):
    @override
    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        if ctx.session.state['error_occurred']:
            return

        if ctx.session.state['tools_count'] > ctx.session.state['tools_count_ori']:
            yield update_state_event(
                ctx,
                state_delta={'tools_count_ori': ctx.session.state['tools_count']},
            )
            yield Event(author=self.name)
        else:
            tool_validator_msg = (
                'System is experiencing tool invocation hallucination; '
                'I recommend retrying with the original parameters.'
            )
            for function_event in context_function_event(
                ctx,
                self.name,
                'matmaster_tool_validator',
                {'msg': tool_validator_msg},
                ModelRole,
            ):
                yield function_event

            current_agent = ctx.agent.parent_agent.parent_agent.name
            if ctx.session.state['tool_hallucination_agent'] != current_agent:
                yield update_state_event(
                    ctx,
                    state_delta={
                        'tool_hallucination': True,
                        'tool_hallucination_agent': ctx.agent.parent_agent.parent_agent.name,
                    },
                )
            else:
                yield update_state_event(
                    ctx,
                    state_delta={
                        'tool_hallucination_agent': None,
                    },
                )

        logger.info(
            f'[{MATMASTER_AGENT_NAME}]:[{self.name}] state = {ctx.session.state}'
        )
