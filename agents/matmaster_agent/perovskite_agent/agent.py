from dp.agent.adapter.adk import CalculationMCPToolset
from google.adk.agents import BaseAgent
from google.adk.tools.mcp_tool.mcp_session_manager import SseServerParams

from agents.matmaster_agent.base_agents.job_agent import (
    BaseAsyncJobAgent,
)
from agents.matmaster_agent.constant import MATMASTER_AGENT_NAME, BohriumStorge, LOCAL_EXECUTOR
from agents.matmaster_agent.logger import matmodeler_logging_handler

from .constant import PEROVSKITE_PLOT_URL, PerovskiteAgentName
from .prompt import (
    PerovskiteAgentDescription,
    PerovskiteAgentInstruction,
)


# Perovskite Plot server uses read-only data & plot tasks; we can use LOCAL executor
perovskite_toolset = CalculationMCPToolset(
    connection_params=SseServerParams(url=PEROVSKITE_PLOT_URL),
    storage=BohriumStorge,  # keep consistent with other agents for possible file outputs
    executor=LOCAL_EXECUTOR,
    async_mode=True,
    wait=False,
    logging_callback=matmodeler_logging_handler,
)


class PerovskiteAgent(BaseAsyncJobAgent):
    """
    Perovskite Solar Cell Data Analysis Agent
    
    Features:
    - Perovskite solar cell data analysis and visualization
    - PCE vs time analysis with interactive scatter plots
    - Solar cell structure trend analysis with stacked bar charts
    - Intelligent device structure classification
    - Excel data processing and validation
    - Interactive Plotly chart generation
    - Statistical analysis and insights
    """
    
    def __init__(self, llm_config):
        super().__init__(
            model=llm_config.deepseek_chat,
            agent_name=PerovskiteAgentName,
            agent_description=PerovskiteAgentDescription,
            agent_instruction=PerovskiteAgentInstruction,
            mcp_tools=[perovskite_toolset],
            dflow_flag=False,
            supervisor_agent=MATMASTER_AGENT_NAME,
        )


def init_perovskite_agent(llm_config=None, use_deepseek=False) -> BaseAgent:
    """Initialize Perovskite Solar Cell Data Analysis Agent"""
    if llm_config is None:
        # If no llm_config provided, use default configuration
        from agents.matmaster_agent.llm_config import MatMasterLlmConfig
        llm_config = MatMasterLlmConfig

    if use_deepseek:
        # Create configuration using DeepSeek
        from agents.matmaster_agent.llm_config import create_default_config
        deepseek_config = create_default_config()
        # Ensure DeepSeek model is initialized
        if hasattr(deepseek_config, 'deepseek_chat'):
            llm_config = deepseek_config

    return PerovskiteAgent(llm_config)


# Create independent root_agent instance for ADK use
try:
    from agents.matmaster_agent.llm_config import MatMasterLlmConfig
    root_agent = init_perovskite_agent(MatMasterLlmConfig, use_deepseek=True)
except ImportError:
    # If import fails, set to None
    root_agent = None


