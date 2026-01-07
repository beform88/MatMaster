from typing import List

import aiohttp

from agents.matmaster_agent.constant import MATMASTER_TOOLS_SERVER


async def get_session_files(session_id: str) -> List[str]:
    url = f'{MATMASTER_TOOLS_SERVER}/api/v1/sessions/{session_id}/files'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            response.raise_for_status()
            json_content = await response.json()

            return json_content.get('data', {}).get('files', [])


async def insert_session_files(session_id: str, files: List[str]) -> List[str]:
    url = f'{MATMASTER_TOOLS_SERVER}/api/v1/sessions/{session_id}/files'
    req = {'files': files}

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=req) as response:
            response.raise_for_status()
            json_content = await response.json()

            return json_content.get('data', {}).get('files', [])


if __name__ == '__main__':
    import asyncio

    result = asyncio.run(insert_session_files('session_id', ['file_url']))
