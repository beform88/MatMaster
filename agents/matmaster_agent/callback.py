import json
import logging
import uuid
from datetime import datetime
from typing import Optional

import litellm
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmResponse
from google.genai import types
from google.genai.types import FunctionCall, Part

from agents.matmaster_agent.base_agents.callback import _get_ak
from agents.matmaster_agent.constant import FRONTEND_STATE_KEY
from agents.matmaster_agent.model import TransferCheck, UserContent
from agents.matmaster_agent.prompt import get_transfer_check_prompt, get_user_content_lang
from agents.matmaster_agent.utils.job_utils import get_job_status, has_job_running, get_running_jobs_detail
from agents.matmaster_agent.utils.llm_response_utils import has_function_call

logger = logging.getLogger(__name__)


# before_agent_callback
async def matmaster_prepare_state(callback_context: CallbackContext) -> Optional[types.Content]:
    callback_context.state['current_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    callback_context.state['error_occurred'] = False
    callback_context.state['origin_job_id'] = None

    callback_context.state[FRONTEND_STATE_KEY] = callback_context.state.get(FRONTEND_STATE_KEY, {})
    callback_context.state[FRONTEND_STATE_KEY]['biz'] = callback_context.state[FRONTEND_STATE_KEY].get('biz', {})
    callback_context.state['long_running_ids'] = callback_context.state.get('long_running_ids', [])
    callback_context.state['long_running_jobs'] = callback_context.state.get('long_running_jobs', {})
    callback_context.state['long_running_jobs_count'] = callback_context.state.get('long_running_jobs_count', 0)
    callback_context.state['long_running_jobs_count_ori'] = callback_context.state.get('long_running_jobs_count_ori', 0)
    callback_context.state['render_job_list'] = callback_context.state.get('render_job_list', False)
    callback_context.state['render_job_id'] = callback_context.state.get('render_job_id', [])
    callback_context.state['dflow'] = callback_context.state.get('dflow', False)
    callback_context.state['ak'] = callback_context.state.get('ak', None)
    callback_context.state['project_id'] = callback_context.state.get('project_id', None)
    callback_context.state['sync_tools'] = callback_context.state.get('sync_tools', None)
    callback_context.state['invocation_id_with_tool_call'] = callback_context.state.get('invocation_id_with_tool_call',
                                                                                        None)
    callback_context.state['special_llm_response'] = False


async def matmaster_set_lang(callback_context: CallbackContext) -> Optional[types.Content]:
    user_content = callback_context.user_content.parts[0].text
    prompt = get_user_content_lang().format(user_content=user_content)
    response = litellm.completion(model='azure/gpt-4o', messages=[{'role': 'user', 'content': prompt}],
                                  response_format=UserContent)
    result: dict = json.loads(response.choices[0].message.content)
    logger.info(f"[matmaster_prepare_state] user_content = {result}")
    language = str(result.get('language', 'zh'))
    callback_context.state['target_language'] = language


# after_model_callback
async def matmaster_check_job_status(callback_context: CallbackContext, llm_response: LlmResponse) -> Optional[
    LlmResponse]:
    if (
            (jobs_dict := callback_context.state['long_running_jobs']) and
            has_job_running(jobs_dict)
    ):
        running_job_ids = get_running_jobs_detail(jobs_dict)
        access_key = _get_ak(callback_context)
        if callback_context.state['target_language'] in ['Chinese', 'zh-CN', '简体中文', 'Chinese (Simplified)']:
            job_complete_intro = '检测到任务 <{job_id}> 已完成，我将立刻转移至对应的 Agent 去获取任务结果。'
        else:
            job_complete_intro = ('Job <{job_id}> has been detected as completed. '
                                  'I will immediately transfer to the corresponding agent to retrieve the job results.')

        reset = False
        for origin_job_id, job_id, job_query_url, agent_name in running_job_ids:
            job_status = get_job_status(job_query_url, access_key=access_key)
            if job_status in ['Failed', 'Finished']:
                if llm_response.partial:  # 原来消息的流式版本置空 None
                    llm_response.content = None
                    break
                if not reset:
                    callback_context.state['special_llm_response'] = True  # 标记开始处理原来消息的非流式版本
                    llm_response.content.parts = []
                    reset = True
                logger.info(f"[matmaster_check_job_status] job_id = {job_id}, job_status = {job_status}")
                function_call_id = f"call_{str(uuid.uuid4()).replace('-', '')[:24]}"
                callback_context.state['origin_job_id'] = origin_job_id
                llm_response.content.parts.append(Part(text=job_complete_intro.format(job_id=job_id)))
                llm_response.content.parts.append(Part(function_call=FunctionCall(id=function_call_id,
                                                                                  name='transfer_to_agent',
                                                                                  args={'agent_name': agent_name})))

        return llm_response


async def matmaster_check_transfer(callback_context: CallbackContext, llm_response: LlmResponse) -> Optional[
    LlmResponse]:
    # 检查响应是否有效
    if not (
            llm_response and
            not llm_response.partial and
            llm_response.content and
            llm_response.content.parts and
            len(llm_response.content.parts) and
            llm_response.content.parts[0].text
    ):
        return None

    prompt = get_transfer_check_prompt().format(response_text=llm_response.content.parts[0].text)
    response = litellm.completion(model='azure/gpt-4o', messages=[{'role': 'user', 'content': prompt}],
                                  response_format=TransferCheck)

    result: dict = json.loads(response.choices[0].message.content)
    is_transfer = bool(result.get('is_transfer', False))
    target_agent = str(result.get('target_agent', ''))

    if (
            is_transfer and
            not has_function_call(llm_response)
    ):
        logger.warning(f"[matmaster_check_transfer] target_agent = {target_agent}")
        function_call_id = f"call_{str(uuid.uuid4()).replace('-', '')[:24]}"
        llm_response.content.parts.append(Part(function_call=FunctionCall(id=function_call_id, name='transfer_to_agent',
                                                                          args={'agent_name': target_agent})))

        return llm_response

    return None
