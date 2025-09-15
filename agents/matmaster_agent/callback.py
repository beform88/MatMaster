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

from agents.matmaster_agent.constant import FRONTEND_STATE_KEY
from agents.matmaster_agent.model import TransferCheck, UserContent
from agents.matmaster_agent.prompt import get_transfer_check_prompt, get_user_content_lang
from agents.matmaster_agent.utils.llm_response_utils import has_function_call

logger = logging.getLogger(__name__)


# before_agent_callback
async def matmaster_prepare_state(callback_context: CallbackContext) -> Optional[types.Content]:
    callback_context.state['current_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    callback_context.state['error_occurred'] = False

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

    user_content = callback_context.user_content.parts[0].text
    prompt = get_user_content_lang().format(user_content=user_content)
    response = litellm.completion(model='azure/gpt-4o', messages=[{'role': 'user', 'content': prompt}],
                                  response_format=UserContent)
    result: dict = json.loads(response.choices[0].message.content)
    logger.info(f"[matmaster_prepare_state] user_content = {result}")
    language = str(result.get('language', 'zh'))
    callback_context.state['target_language'] = language


# after_model_callback
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
        logger.warning(f"Detected Agent Transfer Hallucination, add `transfer_to_agent`")
        function_call_id = f"call_{str(uuid.uuid4()).replace('-', '')[:24]}"
        llm_response.content.parts.append(Part(function_call=FunctionCall(id=function_call_id, name='transfer_to_agent',
                                                                          args={'agent_name': target_agent})))

        return llm_response

    return None
