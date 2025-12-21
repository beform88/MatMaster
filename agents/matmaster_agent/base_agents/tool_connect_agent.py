from typing import AsyncGenerator

from google.adk.agents import InvocationContext
from google.adk.events import Event

from agents.matmaster_agent.base_agents.dntransfer_climit_agent import (
    DisallowTransferAndContentLimitLlmAgent,
)
from agents.matmaster_agent.constant import ModelRole
from agents.matmaster_agent.utils.event_utils import (
    context_function_event,
    is_text,
)


class ToolConnectAgent(DisallowTransferAndContentLimitLlmAgent):
    async def _run_events(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        async for event in super()._run_events(ctx):
            if is_text(event):
                if not event.partial:
                    msg = event.content.parts[0].text

                    for system_job_result_event in context_function_event(
                        ctx,
                        self.name,
                        f'{self.name.replace('_agent', '')}',
                        {'msg': msg},
                        ModelRole,
                    ):
                        yield system_job_result_event
            else:
                yield event
