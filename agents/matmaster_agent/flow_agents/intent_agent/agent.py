from typing import AsyncGenerator

from google.adk.agents import InvocationContext
from google.adk.events import Event

from agents.matmaster_agent.base_agents.schema_agent import (
    DisallowTransferAndContentLimitSchemaAgent,
)
from agents.matmaster_agent.utils.event_utils import handle_upload_file_event


class IntentAgent(DisallowTransferAndContentLimitSchemaAgent):
    async def _run_events(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        async for upload_event in handle_upload_file_event(ctx, self.name):
            yield upload_event

        async for event in super()._run_events(ctx):
            yield event
