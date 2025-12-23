from dp.agent.adapter.adk import CalculationMCPToolset
from google.adk.agents import BaseAgent
from google.adk.tools.mcp_tool.mcp_session_manager import SseServerParams

from agents.matmaster_agent.constant import MATMASTER_AGENT_NAME
from agents.matmaster_agent.core_agents.public_agents.sync_agent import (
    BaseSyncAgentWithToolValidator,
)
from agents.matmaster_agent.llm_config import LLMConfig
from agents.matmaster_agent.logger import matmodeler_logging_handler
from agents.matmaster_agent.sub_agents.NMR_agent.constant import (
    NMR_AGENT_NAME,
    NMR_BOHRIUM_STORAGE,
    NMR_MCP_SERVER_URL,
)
from agents.matmaster_agent.sub_agents.NMR_agent.prompt import (
    NMRAgentDescription,
    NMRAgentInstruction,
)

nmr_toolset = CalculationMCPToolset(
    connection_params=SseServerParams(url=NMR_MCP_SERVER_URL),
    storage=NMR_BOHRIUM_STORAGE,
    logging_callback=matmodeler_logging_handler,
)


class NMRAgent(BaseSyncAgentWithToolValidator):
    def __init__(self, llm_config: LLMConfig):
        super().__init__(
            model=llm_config.default_litellm_model,
            name=NMR_AGENT_NAME,
            description=NMRAgentDescription,
            instruction=NMRAgentInstruction,
            tools=[nmr_toolset],
            render_tool_response=True,
            supervisor_agent=MATMASTER_AGENT_NAME,
            enable_tgz_unpack=False,
        )


def init_nmr_agent(llm_config) -> BaseAgent:
    return NMRAgent(llm_config)
