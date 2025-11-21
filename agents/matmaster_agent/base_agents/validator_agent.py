import logging
from typing import AsyncGenerator, override

from google.adk.agents import InvocationContext
from google.adk.events import Event

from agents.matmaster_agent.base_agents.error_agent import ErrorHandleBaseAgent
from agents.matmaster_agent.constant import MATMASTER_AGENT_NAME, ModelRole
from agents.matmaster_agent.locales import i18n
from agents.matmaster_agent.logger import PrefixFilter
from agents.matmaster_agent.style import tool_retry_failed_card
from agents.matmaster_agent.utils.event_utils import (
    all_text_event,
    context_function_event,
    update_state_event,
)

logger = logging.getLogger(__name__)
logger.addFilter(PrefixFilter(MATMASTER_AGENT_NAME))
logger.setLevel(logging.INFO)


class ValidatorAgent(ErrorHandleBaseAgent):
    validator_key: str

    @override
    async def _run_events(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        if ctx.session.state['error_occurred']:
            return

        if (
            ctx.session.state[self.validator_key]
            > ctx.session.state[f'{self.validator_key}_ori']
        ):
            yield update_state_event(
                ctx,
                state_delta={
                    f'{self.validator_key}_ori': ctx.session.state[self.validator_key],
                    'tool_hallucination': False,
                },
            )
            yield Event(author=self.name)
        else:
            if not ctx.session.state['tool_hallucination']:  # 第一次重试
                message = i18n.t('ToolInvocateHallucinationAction')
                for tool_hallucination_event in context_function_event(
                    ctx,
                    self.name,
                    'materials_tool_hallucination',
                    {'msg': message},
                    ModelRole,
                    None,
                ):
                    yield tool_hallucination_event

                yield update_state_event(
                    ctx,
                    state_delta={
                        'tool_hallucination': True,
                    },
                )
            else:  # 第二次重试
                message = tool_retry_failed_card(i18n=i18n)
                for tool_hallucination_event in all_text_event(
                    ctx,
                    self.name,
                    message,
                    ModelRole,
                ):
                    yield tool_hallucination_event

        logger.info(f'{ctx.session.id} state = {ctx.session.state}')
