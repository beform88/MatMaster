from typing import Optional

from google.adk.tools import BaseTool, ToolContext


async def check_file_url(
    tool: BaseTool, args: dict, tool_context: ToolContext
) -> Optional[dict]:
    if not args['file_url'].startswith('http'):
        raise ValueError('[args:file_url] should start with http')
