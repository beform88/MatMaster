import copy

from dp.agent.adapter.adk import CalculationMCPToolset
from google.adk.agents import BaseAgent
from google.adk.tools.mcp_tool.mcp_session_manager import SseServerParams

from agents.matmaster_agent.base_agents.job_agent import (
    BaseAsyncJobAgent,
    ResultCalculationMCPLlmAgent,
    SubmitCoreCalculationMCPLlmAgent,
)
from agents.matmaster_agent.constant import MATMASTER_AGENT_NAME
from agents.matmaster_agent.logger import matmodeler_logging_handler

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
    """APEX材料性质计算智能体"""
    
    def __init__(self, llm_config):
        # 动态生成包含性质信息的指令
        from .prompt import get_available_properties_info
        
        properties_info = get_available_properties_info()
        eos_info = f"EOS (状态方程): {properties_info['eos']['description']}"
        elastic_info = f"Elastic (弹性性质): {properties_info['elastic']['description']}"
        surface_info = f"Surface (表面形成能): {properties_info['surface']['description']}"
        vacancy_info = f"Vacancy (空位形成能): {properties_info['vacancy']['description']}"
        interstitial_info = f"Interstitial (间隙原子形成能): {properties_info['interstitial']['description']}"
        phonon_info = f"Phonon (声子谱): {properties_info['phonon']['description']}"
        gamma_info = f"Gamma (γ表面): {properties_info['gamma']['description']}"
        
        # 格式化指令
        formatted_instruction = ApexAgentInstruction.format(
            eos_info=eos_info,
            elastic_info=elastic_info,
            surface_info=surface_info,
            vacancy_info=vacancy_info,
            interstitial_info=interstitial_info,
            phonon_info=phonon_info,
            gamma_info=gamma_info
        )
        
        # 使用constant.py中定义的配置
        toolset.storage = ApexBohriumStorage
        toolset.executor = ApexBohriumExecutor
        
        super().__init__(
            model=llm_config.gpt_4o,
            mcp_tools=[toolset],
            agent_name=ApexAgentName,
            agent_description=ApexAgentDescription,
            agent_instruction=formatted_instruction,
            submit_core_agent_class=SubmitCoreCalculationMCPLlmAgent,
            submit_core_agent_name=ApexSubmitCoreAgentName,
            submit_core_agent_description="APEX任务提交核心智能体",
            submit_core_agent_instruction=ApexSubmitCoreAgentInstruction,
            submit_render_agent_name=ApexSubmitRenderAgentName,
            result_core_agent_class=ResultCalculationMCPLlmAgent,
            result_core_agent_name=ApexResultCoreAgentName,
            result_core_agent_instruction=ApexResultCoreAgentInstruction,
            result_transfer_agent_name=ApexResultTransferAgentName,
            result_transfer_agent_instruction="处理APEX计算结果传输",
            transfer_agent_name=ApexTransferAgentName,
            transfer_agent_instruction=ApexTransferAgentInstruction,
            submit_agent_name=ApexSubmitAgentName,
            submit_agent_description=ApexSubmitAgentDescription,
            result_agent_name=ApexResultAgentName,
            result_agent_description=ApexResultAgentDescription,
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
            print("使用DeepSeek模型配置")
            llm_config = deepseek_config

    return ApexAgent(llm_config)


# 创建独立的root_agent实例供ADK使用
try:
    from agents.matmaster_agent.llm_config import MatMasterLlmConfig
    root_agent = init_apex_agent(MatMasterLlmConfig, use_deepseek=True)
except ImportError:
    # 如果导入失败，设置为None
    root_agent = None