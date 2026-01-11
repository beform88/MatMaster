from typing import AsyncGenerator

from google.adk.agents import InvocationContext
from google.adk.events import Event

from agents.matmaster_agent.core_agents.base_agents.error_agent import (
    ErrorHandleBaseAgent,
)
from agents.matmaster_agent.utils.event_utils import handle_upload_file_event


class HandleUploadAgent(ErrorHandleBaseAgent):
    async def _run_events(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        async for upload_event in handle_upload_file_event(ctx, self.name):
            yield upload_event
