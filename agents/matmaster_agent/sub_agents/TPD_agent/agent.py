from dp.agent.adapter.adk import CalculationMCPToolset
from google.adk.agents import BaseAgent
from google.adk.tools.mcp_tool.mcp_session_manager import SseServerParams

from agents.matmaster_agent.constant import MATMASTER_AGENT_NAME
from agents.matmaster_agent.core_agents.public_agents.sync_agent import (
    BaseSyncAgentWithToolValidator,
)
from agents.matmaster_agent.llm_config import LLMConfig
from agents.matmaster_agent.logger import matmodeler_logging_handler
from agents.matmaster_agent.sub_agents.TPD_agent.constant import (
    TPD_AGENT_NAME,
    TPD_BOHRIUM_STORAGE,
    TPD_MCP_SERVER_URL,
)
from agents.matmaster_agent.sub_agents.TPD_agent.prompt import (
    TPDAgentDescription,
    TPDAgentInstruction,
)

tpd_toolset = CalculationMCPToolset(
    connection_params=SseServerParams(url=TPD_MCP_SERVER_URL),
    storage=TPD_BOHRIUM_STORAGE,
    logging_callback=matmodeler_logging_handler,
)


class TPDAgent(BaseSyncAgentWithToolValidator):
    def __init__(self, llm_config: LLMConfig):
        super().__init__(
            model=llm_config.default_litellm_model,
            name=TPD_AGENT_NAME,
            description=TPDAgentDescription,
            instruction=TPDAgentInstruction,
            tools=[tpd_toolset],
            render_tool_response=True,
            supervisor_agent=MATMASTER_AGENT_NAME,
        )


def init_tpd_agent(llm_config) -> BaseAgent:
    return TPDAgent(llm_config)