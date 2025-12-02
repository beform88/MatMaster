from dp.agent.adapter.adk import CalculationMCPToolset
from google.adk.agents import BaseAgent
from google.adk.tools.mcp_tool.mcp_session_manager import SseServerParams

from agents.matmaster_agent.base_agents.public_agent import (
    BaseSyncAgentWithToolValidator,
)
from agents.matmaster_agent.constant import MATMASTER_AGENT_NAME
from agents.matmaster_agent.llm_config import LLMConfig
from agents.matmaster_agent.logger import matmodeler_logging_handler
from agents.matmaster_agent.sub_agents.Physical_adsorption_agent.constant import (
    Physical_Adsorption_AGENT_NAME,
    Physical_Adsorption_BOHRIUM_STORAGE,
    Physical_Adsorption_MCP_SERVER_URL,
)
from agents.matmaster_agent.sub_agents.Physical_adsorption_agent.prompt import (
    Physical_Adsorption_AgentDescription,
    Physical_Adsorption_AgentInstruction,
)

physical_adsorption_toolset = CalculationMCPToolset(
    connection_params=SseServerParams(url=Physical_Adsorption_MCP_SERVER_URL),
    storage=Physical_Adsorption_BOHRIUM_STORAGE,
    logging_callback=matmodeler_logging_handler,
)


class PhysicalAdsorptionAgent(BaseSyncAgentWithToolValidator):
    def __init__(self, llm_config: LLMConfig):
        super().__init__(
            model=llm_config.default_litellm_model,
            name=Physical_Adsorption_AGENT_NAME,
            description=Physical_Adsorption_AgentDescription,
            instruction=Physical_Adsorption_AgentInstruction,
            tools=[physical_adsorption_toolset],
            render_tool_response=True,
            supervisor_agent=MATMASTER_AGENT_NAME,
        )


def init_physical_adsorption_agent(llm_config) -> BaseAgent:
    return PhysicalAdsorptionAgent(llm_config)
