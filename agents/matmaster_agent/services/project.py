import asyncio
import json

import aiohttp

from agents.matmaster_agent.constant import OPENAPI_HOST


async def get_project_list(access_key: str):
    user_project_list_url = f"{OPENAPI_HOST}/openapi/v1/open/user/project/list"
    params = {'accessKey': access_key}

    async with aiohttp.ClientSession() as session:
        async with session.get(user_project_list_url, params=params) as response:
            res = json.loads(await response.text())
            project_list = res.get('data', {}).get('items', [])

            if project_list:
                return [item['project_id'] for item in project_list]
            else:
                return project_list


if __name__ == '__main__':
    result = asyncio.run(get_project_list('ba5cdc51b4934d1689e38332b27bb271'))
