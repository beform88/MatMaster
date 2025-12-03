from typing import TypedDict

import aiohttp

from agents.matmaster_agent.utils.io_oss import extract_file_content


class FileParseResponse(TypedDict):
    msg: str


async def file_parse(file_url: str) -> FileParseResponse:
    """解析文件url，返回总结内容"""
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
    async with aiohttp.ClientSession() as session:
        async with session.head(file_url, allow_redirects=True) as resp:
            size = resp.headers.get('Content-Length')
            if int(size) <= MAX_FILE_SIZE:
                msg = f'{await extract_file_content(file_url)}'
            else:
                msg = f'文件超出大小限制，{MAX_FILE_SIZE}'

    return FileParseResponse(msg=msg)
