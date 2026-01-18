import asyncio
import base64
import mimetypes
from typing import TypedDict

import aiohttp
from litellm import acompletion

from agents.matmaster_agent.utils.io_oss import extract_file_content, get_filename_from_url
from agents.matmaster_agent.sub_agents.built_in_agent.file_parse_agent.prompt import FileParseAgentInstruction
from agents.matmaster_agent.llm_config import MODEL_MAPPING

class FileParseResponse(TypedDict):
    msg: str


async def file_parse(file_url: str) -> FileParseResponse:
    """解析文件url，返回总结内容。支持文本和图片解析。"""
    # 调整为 20MB 以支持高清图片
    MAX_FILE_SIZE = 20 * 1024 * 1024  

    async with aiohttp.ClientSession() as session:
        try:
            # 1. 下载文件内容并检查大小
            # 注意：这里直接读取到内存，如果是超大文件可能会有风险，但 controlled by MAX_FILE_SIZE
            async with session.get(
                file_url, timeout=aiohttp.ClientTimeout(total=60)
            ) as resp:
                if resp.content_length and resp.content_length > MAX_FILE_SIZE:
                     return FileParseResponse(msg=f'文件超出大小限制（>{MAX_FILE_SIZE} 字节）')
                
                content = await resp.read()
                if len(content) > MAX_FILE_SIZE:
                    return FileParseResponse(msg=f'文件超出大小限制（>{MAX_FILE_SIZE} 字节）')

            # 2. 判断文件类型
            filename = await get_filename_from_url(file_url)
            mime_type, _ = mimetypes.guess_type(filename)
            
            # 3. 如果是图片，调用 Gemini-3-Pro 进行视觉解析
            if mime_type and mime_type.startswith('image/'):
                # 构造 Base64 Data URI
                b64_data = base64.b64encode(content).decode('utf-8')
                data_uri = f"data:{mime_type};base64,{b64_data}"
                
                # 获取配置中的 Gemini 模型名称
                # 优先使用配置映射，如果没有则使用默认预览版字符串
                # 使用正确的键值对格式查找模型
                model_key = ('litellm_proxy', 'gemini-3-pro')
                model = MODEL_MAPPING.get(model_key, "litellm_proxy/gemini-3-pro-preview")
                
                # 调用 LiteLLM
                # 必须将 Prompt 作为 text，图片作为 image_url 传入
                response = await acompletion(
                    model=model,
                    messages=[{
                        "role": "user",
                        "content": [
                            {"type": "text", "text": FileParseAgentInstruction},
                            {"type": "image_url", "image_url": {"url": data_uri}}
                        ]
                    }],
                    temperature=0.0 # 保持确定性
                )
                
                # 直接返回 Vision 模型的解析结果（JSON字符串）
                return FileParseResponse(msg=response.choices[0].message.content)

            # 4. 如果不是图片，回退到原有的文本提取逻辑
            # extract_file_content 内部会重新下载一次，但这保持了对原 io_oss 逻辑的兼容
            msg = f'{await extract_file_content(file_url)}'
            return FileParseResponse(msg=msg)
            
        except asyncio.TimeoutError:
            return FileParseResponse(msg='请求超时，请检查网络或文件地址')
        except Exception as e:
            # 捕获 litellm 异常或其他网络异常
            return FileParseResponse(msg=f'解析错误: {str(e)}')


if __name__ == '__main__':
    # text file
    asyncio.run(
        file_parse(
            'https://dp-storage-test2.oss-cn-zhangjiakou.aliyuncs.com/bohrium-test/bohrium/feedback/attachment/01KBM1X4KGDHTE2ZR44G7EHC0Z/dsc-example.txt'
        )
    )
    
    # image file
    asyncio.run(
        file_parse(
            'https://dp-storage-test2.oss-cn-zhangjiakou.aliyuncs.com/bohrium-test/bohrium/feedback/attachment/01KBM1X4KGDHTE2ZR44G7EHC0Z/microscopy_image.png'
        )
    )