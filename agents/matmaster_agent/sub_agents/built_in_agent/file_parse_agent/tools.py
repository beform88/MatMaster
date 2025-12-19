from typing import TypedDict

import aiohttp

from agents.matmaster_agent.utils.io_oss import extract_file_content


class FileParseResponse(TypedDict):
    msg: str


async def file_parse(file_url: str) -> FileParseResponse:
    """解析文件url，返回总结内容"""
    MAX_FILE_SIZE = 1 * 1024 * 1024  # 1 MB

    async with aiohttp.ClientSession() as session:
        try:
            # 先下载文件检查大小
            async with session.get(
                file_url, timeout=aiohttp.ClientTimeout(total=30)
            ) as resp:
                received = 0

                # 只检查大小，不保存内容
                async for chunk in resp.content.iter_chunked(8192):
                    received += len(chunk)
                    if received > MAX_FILE_SIZE:
                        return FileParseResponse(
                            msg=f'文件超出大小限制（>{MAX_FILE_SIZE} 字节）'
                        )
                    # 如果只想检查大小，可以在这里 break
                    # 但注意：中断连接可能需要特殊处理

            # 如果文件大小在限制内，调用 extract_file_content
            # 注意：这里 extract_file_content 会重新下载文件
            msg = f'{await extract_file_content(file_url)}'
            return FileParseResponse(msg=msg)
        except asyncio.TimeoutError:
            return FileParseResponse(msg='请求超时，请检查网络或文件地址')
        except aiohttp.ClientError as e:
            return FileParseResponse(msg=f'网络请求错误: {str(e)}')


if __name__ == '__main__':
    import asyncio

    asyncio.run(
        file_parse(
            'https://dp-storage-test2.oss-cn-zhangjiakou.aliyuncs.com/bohrium-test/bohrium/feedback/attachment/01KBM1X4KGDHTE2ZR44G7EHC0Z/dsc-example.txt'
        )
    )
