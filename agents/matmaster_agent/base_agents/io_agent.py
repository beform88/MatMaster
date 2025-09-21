from typing import AsyncGenerator, override

from google.adk.agents import LlmAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event

from agents.matmaster_agent.constant import ModelRole
from agents.matmaster_agent.utils.event_utils import context_function_event


class HandleFileUploadLlmAgent(LlmAgent):
    """An LLM agent that handles file uploads along with text prompts.

    This agent extends the base LlmAgent to process both text content and file uploads
    in the user's input. It constructs a prompt that includes references to any uploaded files
    before delegating to the parent class's implementation.

    Attributes:
        Inherits all attributes from LlmAgent.
    """

    @override
    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        """Asynchronously process the invocation context with file upload support.

        Processes the user content parts, extracting text and file references to construct
        a comprehensive prompt. Files are referenced by their URIs in the prompt. Yields
        system events with the constructed prompt before delegating to the parent implementation.

        Args:
            ctx: The invocation context containing user content and metadata.

        Yields:
            Event: First yields a system event with the constructed prompt (including file references),
                  then yields all events from the parent implementation.

        Note:
            - Text parts are concatenated directly into the prompt
            - File data parts are referenced by their file_uri in the prompt
            - Inline data parts are currently ignored
        """
        prompt = ''
        if ctx.user_content and ctx.user_content.parts:
            for part in ctx.user_content.parts:
                if part.text:
                    prompt += part.text
                elif part.inline_data:
                    pass  # Inline data is currently not processed
                elif part.file_data:
                    prompt += f", file_url = {part.file_data.file_uri}"

                    # 包装成function_call，来避免在历史记录中展示
                    for event in context_function_event(
                        ctx,
                        self.name,
                        'system_upload_file',
                        {'prompt': prompt},
                        ModelRole,
                    ):
                        yield event

        # Delegate to parent implementation for the actual processing
        async for event in super()._run_async_impl(ctx):
            yield event
