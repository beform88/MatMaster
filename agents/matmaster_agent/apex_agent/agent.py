import copy
import json
from typing import Any, Dict

from dp.agent.adapter.adk import CalculationMCPToolset
from google.adk.agents import BaseAgent
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.mcp_tool.mcp_session_manager import SseServerParams
from google.adk.tools.tool_context import ToolContext
from mcp.types import CallToolResult

from agents.matmaster_agent.base_agents.job_agent import (
    BaseAsyncJobAgent,
    CalculationMCPLlmAgent,
    ResultCalculationMCPLlmAgent,
    SubmitCoreCalculationMCPLlmAgent,
)
from agents.matmaster_agent.constant import MATMASTER_AGENT_NAME
from agents.matmaster_agent.logger import matmodeler_logging_handler
from agents.matmaster_agent.utils.helper_func import is_json

from .constant import (
    ApexServerUrl,
    ApexBohriumExecutor,
    ApexBohriumStorage,
    ApexAgentName,
)
from .prompt import (
    ApexAgentDescription,
    ApexAgentInstruction,
    ApexSubmitAgentName,
    ApexSubmitAgentDescription,
    ApexSubmitCoreAgentName,
    ApexSubmitCoreAgentInstruction,
    ApexSubmitRenderAgentName,
    ApexResultAgentName,
    ApexResultAgentDescription,
    ApexResultCoreAgentName,
    ApexResultCoreAgentInstruction,
    ApexResultTransferAgentName,
    ApexTransferAgentName,
    ApexTransferAgentInstruction,
)


async def before_tool_callback(tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext):
    """工具调用前的回调函数"""
    agent_name = tool_context.agent_name
    tool_name = tool.name
    print(f"[Callback] Before tool call for tool '{tool_name}' in agent '{agent_name}'")
    print(f"[Callback] Args: {args}")


async def after_tool_callback(tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext,
                              tool_response: CallToolResult):
    """APEX计算结果的后处理，将图片文件自动渲染为Markdown格式"""
    tool_info = {
        "after": {
            'tool_name': tool.name,
            'tool_args': args,
            'tool_response': tool_response.content[0].text if (tool_response and len(tool_response.content)) else None
        }
    }

    # 检查是否有有效的响应数据
    if not (tool_response and
            tool_response.content and
            tool_response.content[0].text):
        print("[Callback] Tool response is empty")
        return None

    try:
        response_text = tool_response.content[0].text
        
        # 检查是否是JSON格式的响应
        if is_json(response_text):
            response_data = json.loads(response_text)
            
            # 检查是否包含图表图片数据
            if 'chart_image' in response_data and response_data['chart_image']:
                # 生成markdown图片格式
                markdown_image = f"![apex_chart]({response_data['chart_image']})"
                tool_info['after']['tool_response'] = markdown_image
                print(f"[Callback] Generated markdown image for {tool.name}")
                return markdown_image
            
            # 检查是否包含其他图片数据
            elif 'plot' in response_data and response_data['plot']:
                markdown_image = f"![apex_plot]({response_data['plot']})"
                tool_info['after']['tool_response'] = markdown_image
                print(f"[Callback] Generated markdown plot for {tool.name}")
                return markdown_image
            
            # 检查是否包含markdown报告（可能已经包含图片）
            elif 'markdown_report' in response_data and response_data['markdown_report']:
                print(f"[Callback] Found markdown report in {tool.name} response")
                return response_data['markdown_report']
        
        # 如果不是JSON或没有图片数据，返回原始响应
        return response_text
        
    except Exception as e:
        print(f"[Callback] Failed to process tool response: {str(e)}")
        return tool_response.content[0].text if tool_response.content else None


# 配置SSE参数
sse_params = SseServerParams(url=ApexServerUrl)
toolset = CalculationMCPToolset(
    connection_params=sse_params,
    storage=None,  # 将在运行时动态设置
    executor=None,  # 将在运行时动态设置
    async_mode=True,
    wait=False,
    logging_callback=matmodeler_logging_handler
)


class ApexAgent(BaseAsyncJobAgent):
    """
    APEX材料性质计算智能体 (v4更新)
    
    支持功能：
    - 材料性质计算（空位、间隙、弹性、表面、EOS、声子、γ表面）
    - 异步Bohrium任务提交和状态监控
    - 智能用户意图识别和参数转换
    - 结构文件管理和下载
    - 存储空间管理
    - Bohrium认证信息动态配置
    - 自动图片渲染为Markdown格式
    - 异步任务处理（继承BaseAsyncJobAgent）
    """
    
    def __init__(self, llm_config):
        # 使用constant.py中定义的配置（v4更新）
        toolset.storage = ApexBohriumStorage
        toolset.executor = ApexBohriumExecutor
        
        # 创建支持回调函数的MCP工具集
        callback_toolset = CalculationMCPToolset(
            connection_params=sse_params,
            storage=ApexBohriumStorage,
            executor=ApexBohriumExecutor,
            async_mode=True,
            wait=False,
            logging_callback=matmodeler_logging_handler,
            before_tool_callback=before_tool_callback,
            after_tool_callback=after_tool_callback
        )
        
        super().__init__(
            model=llm_config.gpt_4o,
            agent_name=ApexAgentName,
            agent_description=ApexAgentDescription,
            agent_instruction=ApexAgentInstruction,  # 直接使用静态指令，不再动态格式化
            mcp_tools=[callback_toolset],  # 使用支持回调函数的工具集
            dflow_flag=False,  # APEX使用Bohrium异步任务，不使用dflow
            supervisor_agent=MATMASTER_AGENT_NAME
        )


def init_apex_agent(llm_config=None, use_deepseek=False) -> BaseAgent:
    """初始化APEX材料性质计算智能体"""
    if llm_config is None:
        # 如果没有提供llm_config，使用默认配置
        from agents.matmaster_agent.llm_config import MatMasterLlmConfig
        llm_config = MatMasterLlmConfig

    if use_deepseek:
        # 创建使用DeepSeek的配置
        from agents.matmaster_agent.llm_config import create_default_config
        deepseek_config = create_default_config()
        # 确保DeepSeek模型已初始化
        if hasattr(deepseek_config, 'deepseek_chat'):
            llm_config = deepseek_config

    return ApexAgent(llm_config)


# 创建独立的root_agent实例供ADK使用
try:
    from agents.matmaster_agent.llm_config import MatMasterLlmConfig
    root_agent = init_apex_agent(MatMasterLlmConfig, use_deepseek=True)
except ImportError:
    # 如果导入失败，设置为None
    root_agent = None