import asyncio

from google.adk.tools._gemini_schema_util import _to_gemini_schema
from mcp import ClientSession
from mcp.client.sse import sse_client
from mcp.client.streamable_http import streamablehttp_client


async def get_tool_function_declaration(url: str, tool_name: str, method: str = 'sse'):
    client_cm = sse_client(url) if method == 'sse' else streamablehttp_client(url)

    async with client_cm as streams:
        # sse 长度为 2，http 长度为 3，直接取前两个
        read, write = streams[0], streams[1]
        async with ClientSession(read, write) as session:
            # 初始化
            await session.initialize()

            # 调用 tools/list 方法（对应 get_tools）
            result = await session.list_tools()
            target_tool = [tool for tool in result.tools if tool.name == tool_name][0]
            result = _to_gemini_schema(target_tool.inputSchema).to_json_dict()
            print(result)


if __name__ == '__main__':
    # sse
    url = 'http://toyl1410396.bohrium.tech:50001/sse'
    asyncio.run(get_tool_function_declaration(url, tool_name='abacus_dos_run'))

    # streamable http
    url = 'https://structure-generator-uuid1767674194.appspace.bohrium.com/mcp?token=a297dc122dc74368af3d2e725991d559'
    asyncio.run(
        get_tool_function_declaration(url, tool_name='add_hydrogens', method='mcp')
    )
