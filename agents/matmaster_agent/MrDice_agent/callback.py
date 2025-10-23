import logging
import os
import json
from typing import Optional
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmResponse

logger = logging.getLogger(__name__)


async def mrdice_subagent_force_execution(
    tool, args, tool_context, tool_response
) -> Optional[dict]:
    """
    MrDice 子代理强制执行 callback
    
    统一解决幻觉和确认问题：
    1. 如果工具调用失败 → 强制执行工具调用
    2. 如果没有真实的检索结果 → 强制执行工具调用
    """
    # 只对 MrDice 子代理生效
    agent_name = tool_context.state.get('current_agent_name', '')
    if not agent_name.endswith(('_agent', '_Agent')):
        return None
    
    logger.info(f"[mrdice_subagent_force_execution] Checking agent: {agent_name}")
    
    # 检查1: 工具调用是否成功
    if not tool_response or tool_response.get('status') != 'success':
        logger.warning(f"[mrdice_subagent_force_execution] Tool call failed, forcing execution")
        return await tool.run_async(args=args, tool_context=tool_context)
    
    # 检查2: 是否有真实的检索结果
    result_data = tool_response.get('result', {})
    n_found = result_data.get('n_found')
    output_dir = result_data.get('output_dir')
    
    # 统一检查：n_found 有效 + output_dir 存在 + summary.json 存在
    if (n_found is None or not isinstance(n_found, int) or n_found < 0 or
        not output_dir or not os.path.exists(output_dir) or
        not os.path.exists(os.path.join(output_dir, 'summary.json'))):
        logger.warning(f"[mrdice_subagent_force_execution] Invalid result data, forcing execution")
        return await tool.run_async(args=args, tool_context=tool_context)
    
    # 所有检查都通过，返回原始结果
    logger.info(f"[mrdice_subagent_force_execution] Validation passed: n_found={n_found}")
    return None


def create_mrdice_subagent_callback():
    """
    创建 MrDice 子代理专用的 callback
    
    返回一个 after_tool_callback，统一处理：
    1. 工具调用失败检测和重试
    2. 结果数据有效性检测和强制执行
    """
    return mrdice_subagent_force_execution
