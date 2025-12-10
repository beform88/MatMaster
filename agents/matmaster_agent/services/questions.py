import random
from typing import List

import aiohttp

from agents.matmaster_agent.constant import MATMASTER_TOOLS_SERVER


async def get_random_questions(k: int = 5, i18n=None) -> List[dict]:
    url = f'{MATMASTER_TOOLS_SERVER}/api/v1/questions/'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            response.raise_for_status()
            json_content = await response.json()

            # 过滤掉有 structure_url 的项
            field = 'question' if i18n.language == 'zh' else 'question_en'
            candidates = [
                item[field]
                for item in json_content.get('data', [])
                if not item.get('structure_url')
            ]

            # 若候选数不足 k，则全部返回
            if len(candidates) <= k:
                return candidates

            # 随机返回 k 个
            return random.sample(candidates, k)


if __name__ == '__main__':
    import asyncio

    result = asyncio.run(get_random_questions())
