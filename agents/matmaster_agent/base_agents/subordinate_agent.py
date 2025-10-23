from typing import AsyncGenerator, Optional

from google.adk.agents import InvocationContext
from google.adk.events import Event
from pydantic import Field

from agents.matmaster_agent.base_agents.error_handle_agent import ErrorHandleAgent
from agents.matmaster_agent.constant import ModelRole
from agents.matmaster_agent.utils.event_utils import (
    context_function_event,
)


class SubordinateAgent(ErrorHandleAgent):
    supervisor_agent: Optional[str] = Field(
        None, description='Which one is the supervisor_agent'
    )

    def __init__(self, supervisor_agent, **kwargs):
        super().__init__(supervisor_agent=supervisor_agent, **kwargs)

        self.supervisor_agent = supervisor_agent

    async def _process_events(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        """可重写的方法，专门处理事件循环"""
        async for event in super()._process_events(ctx):
            yield event

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
