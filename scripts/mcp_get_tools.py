import asyncio
import time

from mcp import ClientSession
from mcp.client.sse import sse_client


async def get_tools(type='mcphub'):
    if type == 'mcphub':
        url = 'https://cystalformer-uuid1754551471.app-space.dplink.cc/sse?token=1750cd294e6c4270946ae37107a725ff'
    else:
        url = 'http://pfmx1355864.bohrium.tech:50003/sse'
    async with sse_client(url) as (read, write):
        async with ClientSession(read, write) as session:
            # 初始化
            await session.initialize()

            # 调用 tools/list 方法（对应 get_tools）
            result = await session.list_tools()
            print('Available tools:', result.tools)


if __name__ == '__main__':
    print(time.time())
    asyncio.run(get_tools(type='node'))
    print('node', time.time())
    asyncio.run(get_tools(type='mcphub'))
    print('mcphub', time.time())
