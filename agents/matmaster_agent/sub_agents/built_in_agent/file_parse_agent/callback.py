import logging
from typing import Optional

from google.adk.tools import BaseTool, ToolContext

from agents.matmaster_agent.constant import MATMASTER_AGENT_NAME
from agents.matmaster_agent.logger import PrefixFilter
from agents.matmaster_agent.services.session_files import get_session_files

logger = logging.getLogger(__name__)
logger.addFilter(PrefixFilter(MATMASTER_AGENT_NAME))
logger.setLevel(logging.INFO)


async def check_and_modify_file_url(
    tool: BaseTool, args: dict, tool_context: ToolContext
) -> Optional[dict]:
    if not args['file_url'].startswith('http'):
        session_files = await get_session_files(tool_context.session.id)
        current_file_url = args['file_url']
        for actual_file_url in session_files:
            if current_file_url in actual_file_url or actual_file_url.endswith(
                '/' + current_file_url
            ):
                args['file_url'] = actual_file_url
                logger.warning(
                    f"{tool_context.session.id} file url error, {current_file_url} -> {actual_file_url}"
                )
                break
        logger.error(
            f"{tool_context.session.id} file url error, {current_file_url} not change"
        )
