from dp.agent.adapter.adk import CalculationMCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import SseServerParams

from agents.matmaster_agent.base_agents.job_agent import (
    CalculationMCPLlmAgent,
)
from agents.matmaster_agent.constant import BohriumStorge

from .constant import PEROVSKITE_PLOT_URL, PerovskiteAgentName
from .prompt import (
    PerovskiteAgentDescription,
    PerovskiteAgentInstruction,
)


perovskite_toolset = CalculationMCPToolset(
    connection_params=SseServerParams(url=PEROVSKITE_PLOT_URL),
    storage=BohriumStorge,
)

def init_perovskite_agent(llm_config, use_deepseek: bool = False):
    """Initialize Perovskite Solar Cell Data Analysis Agent using CalculationMCPLlmAgent."""
    # Choose model per flag with sensible fallbacks
    if use_deepseek :
        model = llm_config.deepseek_chat
    else:
        model = llm_config.gpt_4o

    return CalculationMCPLlmAgent(
        model=model,
        name=PerovskiteAgentName,
        description=PerovskiteAgentDescription,
        instruction=PerovskiteAgentInstruction,
        tools=[perovskite_toolset],
    )


