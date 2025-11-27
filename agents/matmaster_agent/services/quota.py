import asyncio

import aiohttp

from agents.matmaster_agent.constant import MATMASTER_TOOLS_SERVER


async def check_quota_service(user_id: str):
    headers = {'X-User-Id': user_id}
    url = f'{MATMASTER_TOOLS_SERVER}/api/v1/quota/info'
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            response.raise_for_status()  # 如果状态码不是 200，抛出异常
            json_content = await response.json()
            return json_content


async def use_quota_service(user_id: str):
    url = f'{MATMASTER_TOOLS_SERVER}/api/v1/quota/use'
    headers = {'X-User-Id': user_id}
    request_json = {'user_id': user_id}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=request_json) as response:
            response.raise_for_status()  # 如果状态码不是 200，抛出异常
            json_content = await response.json()
            return json_content


if __name__ == '__main__':
    asyncio.run(check_quota_service('1'))
    # asyncio.run(use_quota_service('1'))
