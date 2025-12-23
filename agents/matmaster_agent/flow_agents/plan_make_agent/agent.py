import logging
from typing import AsyncGenerator, override

from google.adk.agents import InvocationContext
from google.adk.events import Event

from agents.matmaster_agent.base_agents.schema_agent import SchemaAgent
from agents.matmaster_agent.constant import MATMASTER_AGENT_NAME
from agents.matmaster_agent.utils.event_utils import update_state_event
from agents.matmaster_agent.flow_agents.plan_make_agent.utils import (
    normalize_plan_state,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class PlanMakeAgent(SchemaAgent):
    @override
    async def _run_events(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        async for event in super()._run_events(ctx):
            yield event

        logger.info(
            f'[{MATMASTER_AGENT_NAME}] {ctx.session.id} plan = {ctx.session.state["plan"]}'
        )

        normalized_plan = normalize_plan_state(ctx.session.state['plan'])

        yield update_state_event(ctx, state_delta={'plan': normalized_plan})
