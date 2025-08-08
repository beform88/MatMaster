import asyncio
import base64
import json
import logging
import os
import shutil
import tarfile
import time
import traceback
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import aiofiles
import aiohttp
import oss2
import requests
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event, EventActions
from google.genai.types import Content, FunctionCall, FunctionResponse, Part
from oss2.credentials import EnvironmentVariableCredentialsProvider

from agents.matmaster_agent.constant import ModelRole, OPENAPI_HOST, BOHRIUM_API_URL
from agents.matmaster_agent.model import JobResult, JobResultType

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def ak_to_username(access_key: str) -> str:
    url = f"{OPENAPI_HOST}/openapi/v1/account/info"
    headers = {
        "AccessKey": access_key,
        "User-Agent": "Apifox/1.0.0 (https://apifox.com)",
        "Accept": "*/*",
        "Host": f"{OPENAPI_HOST.split('//')[1]}",
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # 抛出HTTP错误异常

        data = response.json()
        if data.get("code") == 0:
            user_data = data.get("data", {})
            email = user_data.get("email", "")
            phone = user_data.get("phone", "")
            if not email and not phone:
                raise ValueError(
                    "Username not found in response. Please bind your email or phone at https://www.bohrium.com/settings/user.")
            username = email if email else phone
            return username
        else:
            raise Exception(f"API error: {data}")
    except requests.RequestException as e:
        raise Exception(f"HTTP request failed: {e}")
    except Exception as e:
        raise Exception(f"Failed to get user info: {e}")


def ak_to_ticket(
        access_key: str,
        expiration: int = 48  # 48 hours
) -> str:
    url = f"{BOHRIUM_API_URL}/bohrapi/v1/ticket/get?expiration={expiration}&preOrderId=0"
    headers = {
        "Brm-AK": access_key,
        "User-Agent": "Apifox/1.0.0 (https://apifox.com)",
        "Accept": "*/*",
        "Host": f"{BOHRIUM_API_URL.split('//')[1]}",
        "Connection": "keep-alive"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data.get("code") == 0:
            ticket = data.get("data", {}).get("ticket", "")
            if not ticket:
                raise ValueError("Ticket not found in response.")
            return ticket
        else:
            raise Exception(f"API error: {data}")
    except requests.RequestException as e:
        raise Exception(f"HTTP request failed: {e}")
    except Exception as e:
        raise Exception(f"Failed to get ticket: {e}")


async def extract_convert_and_upload(tgz_url: str, temp_dir: str = "./tmp") -> dict:
    """
    使用当前目录下的临时文件夹处理文件
    :param tgz_url: 要下载的tgz文件URL
    :param temp_dir: 临时目录路径（默认当前目录下的tmp文件夹）
    :return: 上传结果字典
    """
    # 创建临时目录（如果不存在）
    temp_path = Path(temp_dir)
    temp_path.mkdir(exist_ok=True, parents=True)

    try:
        # 获取所有JPG文件的Base64编码
        jpg_files = await extract_jpg_from_tgz_url(tgz_url, temp_path)
        conversion_tasks = [jpg_to_base64(jpg) for jpg in jpg_files]
        base64_results = await asyncio.gather(*conversion_tasks)

        # 准备上传任务
        upload_tasks = []
        for jpg_path, b64_data in base64_results:
            filename = jpg_path.name
            oss_path = f"retrosyn/image_{filename}_{int(time.time())}.jpg"
            upload_tasks.append(upload_to_oss_wrapper(b64_data, oss_path, filename))

        return {filename: result for item in await asyncio.gather(*upload_tasks) for filename, result in item.items()}
    finally:
        # 清理临时目录
        shutil.rmtree(temp_path, ignore_errors=True)


async def upload_to_oss_wrapper(b64_data: str, oss_path: str, filename: str) -> Dict[str, dict]:
    def _sync_upload_base64_to_oss(data: str, oss_path: str) -> dict:
        try:
            auth = oss2.ProviderAuth(EnvironmentVariableCredentialsProvider())
            endpoint = os.environ["OSS_ENDPOINT"]
            bucket_name = os.environ["OSS_BUCKET_NAME"]
            bucket = oss2.Bucket(auth, endpoint, bucket_name)

            bucket.put_object(oss_path, base64.b64decode(data))
            return {
                "status": "success",
                "oss_path": f"https://{bucket_name}.oss-cn-zhangjiakou.aliyuncs.com/{oss_path}",
            }
        except Exception as e:
            logger.exception(
                f"[upload_base64_to_oss] OSS 上传失败: oss_path={oss_path} error={str(e)}"
            )
            return {"status": "failed", "reason": str(e)}

    async def upload_base64_to_oss(data: str, oss_path: str) -> dict:
        return await asyncio.to_thread(_sync_upload_base64_to_oss, data, oss_path)

    """上传包装器，保留原始文件名信息"""
    result = await upload_base64_to_oss(b64_data, oss_path)

    return {filename: result}


async def jpg_to_base64(jpg_path: Path) -> Tuple[Path, str]:
    """异步将JPG文件转换为Base64编码"""
    async with aiofiles.open(jpg_path, 'rb') as f:
        content = await f.read()
        return (jpg_path, base64.b64encode(content).decode('utf-8'))


async def extract_jpg_from_tgz_url(tgz_url: str, temp_path: Path) -> List[Path]:
    """使用指定临时目录处理文件"""
    async with aiohttp.ClientSession() as session:
        tgz_path = temp_path / "downloaded.tgz"

        await download_file(session, tgz_url, tgz_path)
        await extract_tarfile(tgz_path, temp_path)

        return await find_jpg_files(temp_path)


async def download_file(session: aiohttp.ClientSession, url: str, dest: Path) -> None:
    """异步下载文件"""
    async with session.get(url) as response:
        response.raise_for_status()
        async with aiofiles.open(dest, 'wb') as f:
            async for chunk in response.content.iter_chunked(8192):
                await f.write(chunk)


async def extract_tarfile(tgz_path: Path, extract_to: Path) -> None:
    """异步解压tar文件(实际解压是同步操作)"""
    # 使用run_in_executor避免阻塞事件循环
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(
        None,
        lambda: tarfile.open(tgz_path).extractall(extract_to)
    )


async def find_jpg_files(directory: Path) -> List[Path]:
    """异步查找JPG文件"""
    # 使用run_in_executor避免阻塞事件循环
    loop = asyncio.get_running_loop()

    def _sync_find():
        return list(directory.rglob("*.jpg")) + list(directory.rglob("*.JPG"))

    return await loop.run_in_executor(None, _sync_find)


def is_json(json_str):
    try:
        json.loads(json_str)
    except:
        return False
    return True


# event check funcs
def has_part(event: Event):
    return (
            event and
            event.content and
            event.content.parts and
            len(event.content.parts) and
            event.content.parts[0]
    )


def is_text(event: Event):
    return (
            has_part(event) and
            event.content.parts[0].text
    )


def is_text_and_not_bohrium(event: Event):
    return (
            is_text(event) and
            not event.content.parts[0].text.startswith("<bohrium-chat-msg>")
    )


def is_function_call(event: Event):
    return (
            has_part(event) and
            event.content.parts[0].function_call
    )


def is_function_response(event: Event):
    return (
            has_part(event) and
            event.content.parts[0].function_response
    )


# event send funcs
# 仅前端感知
def frontend_text_event(ctx: InvocationContext, author: str, text: str, role: str):
    return Event(
        author=author,
        branch=ctx.branch,
        invocation_id=ctx.invocation_id,
        content=Content(parts=[Part(text=text)], role=role),
        partial=True)


def frontend_function_call_event(ctx: InvocationContext, author: str, function_call: FunctionCall, role: str):
    return Event(
        author=author,
        invocation_id=ctx.invocation_id,
        content=Content(
            parts=[Part(function_call=FunctionCall(
                id=f"frontend_{function_call.name}",
                name=function_call.name,
                args=function_call.args
            ))],
            role=role,
        ),
        partial=True
    )


def frontend_function_response_event(ctx: InvocationContext, author: str, function_call: FunctionCall, role: str):
    return Event(
        author=author,
        invocation_id=ctx.invocation_id,
        content=Content(
            parts=[Part(function_response=FunctionResponse(
                id=f"frontend_{function_call.name}",
                name=function_call.name,
                response=None
            ))],
            role=role,
        ),
        partial=True
    )


# 仅模型上下文感知
def context_text_event(ctx: InvocationContext, author: str, text: str, role: str):
    return Event(
        author=author,
        branch=ctx.branch,
        invocation_id=ctx.invocation_id,
        content=Content(parts=[Part(text=text)], role=role),
        partial=False)


def context_function_call_event(ctx: InvocationContext, author: str, function_call_id: str, function_call_name: str,
                                role: str, args: Optional[dict] = None):
    return Event(
        author=author,
        invocation_id=ctx.invocation_id,
        content=Content(
            parts=[Part(function_call=FunctionCall(
                id=function_call_id,
                name=function_call_name,
                args=args,
            ))],
            role=role,
        ),
        partial=False
    )


def context_function_response_event(ctx: InvocationContext, author: str, function_call_id: str, function_call_name: str,
                                    response: Optional[dict], role: str):
    return Event(
        author=author,
        invocation_id=ctx.invocation_id,
        content=Content(
            parts=[Part(function_response=FunctionResponse(
                id=function_call_id,
                name=function_call_name,
                response=response
            ))],
            role=role,
        ),
        partial=False
    )


def context_function_event(ctx: InvocationContext, author: str, function_call_name: str, response: Optional[dict],
                           role: str, args: Optional[dict] = None):
    function_call_id = f"call_{str(uuid.uuid4()).replace('-', '')[:24]}"
    yield context_function_call_event(ctx, author, function_call_id, function_call_name, role, args)
    yield context_function_response_event(ctx, author, function_call_id, function_call_name, response, role)


# 数据库 & 前端都感知
def all_text_event(ctx: InvocationContext, author: str, text: str, role: str):
    yield frontend_text_event(ctx, author, text, role)
    yield context_text_event(ctx, author, text, role)


async def update_session_state(ctx: InvocationContext, author: str):
    actions_with_update = EventActions(state_delta=ctx.session.state)
    system_event = Event(invocation_id=ctx.invocation_id, author=author, actions=actions_with_update)
    await ctx.session_service.append_event(ctx.session, system_event)


async def is_matmodeler_file(filename: str) -> bool:
    return (filename.endswith((".cif", ".poscar", ".contcar", ".vasp", ".xyz",
                               ".mol", ".mol2", ".sdf", ".dump", ".lammpstrj")) or
            filename.startswith("lammpstrj") or
            "POSCAR" in filename or
            "CONTCAR" in filename or
            filename == "STRU")


async def is_tuple_float(data) -> bool:
    return isinstance(data, tuple) and all(isinstance(x, float) for x in data)


async def parse_result(result: dict):
    parsed_result = []
    for k, v in result.items():
        if type(v) in [int, float]:
            parsed_result.append(JobResult(name=k, data=v, type=JobResultType.Value).model_dump(mode="json"))
        elif type(v) == str:
            if not v.startswith("http"):
                parsed_result.append(JobResult(name=k, data=v, type=JobResultType.Value).model_dump(mode="json"))
            else:
                filename = v.split("/")[-1]
                if await is_matmodeler_file(filename):
                    parsed_result.append(JobResult(name=k, data=filename,
                                                   type=JobResultType.MatModelerFile, url=v).model_dump(mode="json"))
                else:
                    parsed_result.append(JobResult(name=k, data=filename,
                                                   type=JobResultType.RegularFile, url=v).model_dump(mode="json"))
        elif await is_tuple_float(v):
            parsed_result.append(JobResult(name=k, data=f"{tuple([float(item) for item in v])}",
                                           type=JobResultType.Value).model_dump(mode="json"))
        else:
            parsed_result.append({"status": "error", "msg": f"{k}({type(v)}) is not supported parse"})
    return parsed_result


async def send_error_event(err, ctx, author, error_handle_agent=None):
    if not error_handle_agent:
        error_handle_agent = ctx.agent.parent_agent

    # 构建更详细的错误信息
    error_details = [
        f"Exception Group caught with {len(err.exceptions)} exceptions:",
        f"Message: {str(err)}",
        "\nIndividual exceptions:"
    ]

    # 添加每个子异常的详细信息
    for i, exc in enumerate(err.exceptions, 1):
        error_details.append(f"\nException #{i}:")
        error_details.append(f"Type: {type(exc).__name__}")
        error_details.append(f"Message: {str(exc)}")
        error_details.append(f"Traceback: {''.join(traceback.format_tb(exc.__traceback__))}")

    # 将所有信息合并为一个字符串
    detailed_error = "\n".join(error_details)
    # 包装成function_call，来避免在历史记录中展示；同时模型可以在上下文中感知
    for event in context_function_event(ctx, author, "system_detail_error",
                                        {"msg": detailed_error}, ModelRole):
        yield event

    async for error_event in error_handle_agent.run_async(ctx):
        yield error_event
