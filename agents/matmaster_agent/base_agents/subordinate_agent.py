from typing import Optional

from google.adk.agents import InvocationContext
from pydantic import Field

from agents.matmaster_agent.base_agents.error_agent import ErrorHandleAgent
from agents.matmaster_agent.constant import ModelRole
from agents.matmaster_agent.utils.event_utils import (
    context_function_event,
)


class SubordinateFeaturesMixin:
    supervisor_agent: Optional[str] = Field(
        None, description='Which one is the supervisor_agent'
    )

    def __init__(self, supervisor_agent, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.supervisor_agent = supervisor_agent

    async def _after_events(self, ctx: InvocationContext):
        if self.supervisor_agent:
            for function_event in context_function_event(
                ctx,
                self.name,
                'transfer_to_agent',
                None,
                ModelRole,
                {'agent_name': self.supervisor_agent},
            ):
                yield function_event


# LlmAgent -> ErrorHandleAgent -> SubordinateAgent
class SubordinateAgent(SubordinateFeaturesMixin, ErrorHandleAgent):
    pass
