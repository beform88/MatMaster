from typing import TypedDict


class MessageResponse(TypedDict):
    msg: str


async def file_parse(file_url: str) -> MessageResponse:
    """解析文件url，返回总结内容"""
    return MessageResponse(msg='文件总结内容为：xxxx')
