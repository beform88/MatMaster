import json
import logging
import uuid
from enum import Enum
from typing import Optional, Type

import litellm
from google.adk.agents.callback_context import CallbackContext
from google.adk.agents.llm_agent import AfterModelCallback
from google.adk.models import LlmResponse
from google.genai.types import FunctionCall, Part

from agents.matmaster_agent.MrDice_agent.constant import MrDice_Agent_Name, MrDiceTargetAgentEnum
from agents.matmaster_agent.MrDice_agent.prompt import MrDiceCheckTransferPrompt
from agents.matmaster_agent.utils.llm_response_utils import has_function_call
from agents.matmaster_agent.utils.model_utils import create_transfer_check_model

logger = logging.getLogger(__name__)


def mrdice_check_transfer(prompt: str, target_agent_enum: Type[Enum]) -> AfterModelCallback:
    """
    MrDice 的转移检测 callback
    
    检测 LLM 响应是否包含转移意图，如果没有则自动添加转移指令
    """
    async def wrapper(
        callback_context: CallbackContext, llm_response: LlmResponse
    ) -> Optional[LlmResponse]:
        # 检查响应是否有效
        if not (
            llm_response
            and not llm_response.partial
            and llm_response.content
            and llm_response.content.parts
            and len(llm_response.content.parts)
            and llm_response.content.parts[0].text
        ):
            return None

        llm_prompt = prompt.format(response_text=llm_response.content.parts[0].text)
        response = litellm.completion(
            model='azure/gpt-4o',
            messages=[{'role': 'user', 'content': llm_prompt}],
            response_format=create_transfer_check_model(target_agent_enum),
        )

        if (
            response
            and response.choices
            and response.choices[0]
            and response.choices[0].message
            and response.choices[0].message.content
        ):
            result: dict = json.loads(response.choices[0].message.content)
        else:
            logger.warning(
                f'[{MrDice_Agent_Name}]:[mrdice_check_transfer] LLM completion error, response = {response}'
            )
            return None

        is_transfer = bool(result.get('is_transfer', False))
        target_agent = str(result.get('target_agent', ''))
        reason = str(result.get('reason', ''))
        symbol_name = (
            f"[{callback_context.agent_name.replace('_agent', '')}_check_transfer]"
        )
        logger.info(
            f"[{MrDice_Agent_Name}]:[mrdice_check_transfer] {symbol_name} target_agent = {target_agent}, is_transfer = {is_transfer}, "
            f"response_text = {llm_response.content.parts[0].text}, reason = {reason}"
        )
        
        if is_transfer and not has_function_call(llm_response):
            logger.warning(
                f"[{MrDice_Agent_Name}]:[mrdice_check_transfer] {symbol_name} add `transfer_to_agent`"
            )
            function_call_id = f"added_{str(uuid.uuid4()).replace('-', '')[:24]}"
            llm_response.content.parts.append(
                Part(
                    function_call=FunctionCall(
                        id=function_call_id,
                        name='transfer_to_agent',
                        args={'agent_name': target_agent},
                    )
                )
            )

            return llm_response

        return None

    return wrapper


