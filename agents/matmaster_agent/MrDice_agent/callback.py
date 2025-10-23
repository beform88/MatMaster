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
    logger.info(f"[mrdice_subagent_force_execution] Checking tool: {tool.name}")
    
    # 检查1: 工具调用是否成功
    # tool_response 可能是 dict 或 CallToolResult 对象
    if isinstance(tool_response, dict):
        # 如果是字典，检查 status
        if not tool_response or tool_response.get('status') != 'success':
            logger.warning(f"[mrdice_subagent_force_execution] Tool call failed, forcing execution")
            return await tool.run_async(args=args, tool_context=tool_context)
        
        # 获取结果数据
        result_data = tool_response.get('result', {})
    else:
        # 如果是 CallToolResult 对象，说明工具调用成功
        # 需要解析 CallToolResult 的内容
        if not tool_response or not tool_response.content:
            logger.warning(f"[mrdice_subagent_force_execution] Invalid CallToolResult, forcing execution")
            return await tool.run_async(args=args, tool_context=tool_context)
        
        # 解析 CallToolResult 的内容
        try:
            result_data = json.loads(tool_response.content[0].text)
        except (json.JSONDecodeError, IndexError, AttributeError) as e:
            logger.warning(f"[mrdice_subagent_force_execution] Failed to parse CallToolResult: {e}, forcing execution")
            return await tool.run_async(args=args, tool_context=tool_context)
    
    # 检查2: 是否有真实的检索结果
    n_found = result_data.get('n_found')
    output_dir = result_data.get('output_dir')
    cleaned_structures = result_data.get('cleaned_structures', [])
    
    # 更严格的 output_dir 格式检查
    is_valid_output_dir = (
        output_dir and 
        output_dir.startswith('https://') and 
        output_dir.endswith('.tgz') and
        'oss-cn-' in output_dir and
        '/outputs/output_dir/' in output_dir
    )
    # 核心检查：基于实际输出结构
    # 1. n_found 必须是有效的非负整数
    # 2. cleaned_structures 必须非空（包含实际结构数据）
    # 3. output_dir 必须符合严格的固定格式
    validation_passed = (
        isinstance(n_found, int) and n_found >= 0 and
        cleaned_structures and len(cleaned_structures) > 0 and
        is_valid_output_dir
    )
    
    if not validation_passed:
        logger.warning(f"[mrdice_subagent_force_execution] Validation failed: n_found={n_found} (type: {type(n_found)}), cleaned_structures_len={len(cleaned_structures)}, output_dir_valid={is_valid_output_dir}, forcing execution")
        return await tool.run_async(args=args, tool_context=tool_context)
    
    # 所有检查都通过，返回原始结果
    logger.info(f"[mrdice_subagent_force_execution] Validation passed: n_found={n_found}, structures={len(cleaned_structures)}, output_dir_valid={is_valid_output_dir}")
    return None


def create_mrdice_subagent_callback():
    """
    创建 MrDice 子代理专用的 callback
    
    返回一个 after_tool_callback，统一处理：
    1. 工具调用失败检测和重试
    2. 结果数据有效性检测和强制执行
    """
    return mrdice_subagent_force_execution
