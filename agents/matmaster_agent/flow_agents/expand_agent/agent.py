import logging
from typing import AsyncGenerator, override

from google.adk.agents import InvocationContext
from google.adk.events import Event

from agents.matmaster_agent.base_agents.schema_agent import SchemaAgent
from agents.matmaster_agent.constant import MATMASTER_AGENT_NAME, ModelRole
from agents.matmaster_agent.logger import PrefixFilter
from agents.matmaster_agent.state import EXPAND
from agents.matmaster_agent.utils.event_utils import (
    context_function_event,
    update_state_event,
)

logger = logging.getLogger(__name__)
logger.addFilter(PrefixFilter(MATMASTER_AGENT_NAME))
logger.setLevel(logging.INFO)


class ExpandAgent(SchemaAgent):
    @override
    async def _run_events(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        async for event in super()._run_events(ctx):
            yield event

        # LLM 输出 Schema 兜底
        if not ctx.session.state[EXPAND].get('update_user_content'):
            logger.warning(f'{ctx.session.id} expand LLM Schema Error, use default')
            origin_user_content = ctx.user_content.parts[0].text
            update_expand = {
                'origin_user_content': origin_user_content,
                'update_user_content': origin_user_content,
            }
            yield update_state_event(ctx, {EXPAND: update_expand})

        for expand_event in context_function_event(
            ctx,
            self.name,
            'update_user_content',
            {'update_user_content': ctx.session.state[EXPAND]['update_user_content']},
            ModelRole,
            None,
        ):
            yield expand_event
