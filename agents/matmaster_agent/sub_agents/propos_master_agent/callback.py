import base64
import logging
import time

from google.adk.tools import ToolContext

from agents.matmaster_agent.utils.io_oss import upload_to_oss_wrapper

logger = logging.getLogger(__name__)


async def after_tool_callback(tool, args, tool_context, tool_response):
    print(f"[after_tool_callback] Tool '{tool.name}' executed.")
    return tool_response


async def before_tool_callback(tool, args, tool_context: ToolContext):
    logger.info(f"[proposmaster][before_tool_callback] Tool '{tool.name}' called.")
    logger.info(f"[proposmaster][before_tool_callback] Tool args: {args}")

    session_context_text = ''
    for event in tool_context.session.events:
        if (
            event.content
            and hasattr(event.content, 'parts')
            and len(event.content.parts) > 0
        ):
            session_context_text += str(event.content.parts)
    oss_path = f"proposmaster/context-{tool_context.session.id}-{int(time.time())}.txt"

    upload_result = await upload_to_oss_wrapper(
        base64.b64encode(session_context_text.encode('utf-8')).decode('ascii'),
        oss_path,
        'context_file',
    )
    logger.info(f"[proposmaster][before_tool_callback] context file: {upload_result}]")
    args['context_file_url'] = upload_result['context_file']
    return
