from typing import AsyncGenerator, Optional, override

from google.adk.agents import InvocationContext, LlmAgent
from google.adk.events import Event
from pydantic import Field

from agents.matmaster_agent.constant import ModelRole
from agents.matmaster_agent.utils.event_utils import (
    context_function_event,
    send_error_event,
)


class LlmWrapAgent(LlmAgent):
    supervisor_agent: Optional[str] = Field(
        None, description='Which one is the supervisor_agent'
    )

    def __init__(self, supervisor_agent, **kwargs):
        super().__init__(supervisor_agent=supervisor_agent, **kwargs)

        self.supervisor_agent = supervisor_agent

    @override
    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        try:
            async for event in super()._run_async_impl(ctx):
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
        except BaseException as err:
            async for error_event in send_error_event(err, ctx, self.name):
                yield error_event
