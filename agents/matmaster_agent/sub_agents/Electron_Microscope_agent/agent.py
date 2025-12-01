from dp.agent.adapter.adk import CalculationMCPToolset
from google.adk.agents import BaseAgent
from google.adk.tools.mcp_tool.mcp_session_manager import SseServerParams

from agents.matmaster_agent.base_agents.public_agent import (
    BaseSyncAgentWithToolValidator,
)
from agents.matmaster_agent.constant import MATMASTER_AGENT_NAME
from agents.matmaster_agent.llm_config import LLMConfig
from agents.matmaster_agent.logger import matmodeler_logging_handler
from agents.matmaster_agent.sub_agents.Electron_Microscope_agent.constant import (
    Electron_Microscope_AGENT_NAME,
    Electron_Microscope_BOHRIUM_STORAGE,
    Electron_Microscope_MCP_SERVER_URL,
)
from agents.matmaster_agent.sub_agents.Electron_Microscope_agent.prompt import (
    Electron_Microscope_AgentDescription,
    Electron_Microscope_AgentInstruction,
)

electron_microscope_toolset = CalculationMCPToolset(
    connection_params=SseServerParams(url=Electron_Microscope_MCP_SERVER_URL),
    storage=Electron_Microscope_BOHRIUM_STORAGE,
    logging_callback=matmodeler_logging_handler,
)


class ElectronMicroscopeAgent(BaseSyncAgentWithToolValidator):
    def __init__(self, llm_config: LLMConfig):
        super().__init__(
            model=llm_config.default_litellm_model,
            name=Electron_Microscope_AGENT_NAME,
            description=Electron_Microscope_AgentDescription,
            instruction=Electron_Microscope_AgentInstruction,
            tools=[electron_microscope_toolset],
            render_tool_response=True,
            supervisor_agent=MATMASTER_AGENT_NAME,
        )


def init_electron_microscope_agent(llm_config) -> BaseAgent:
    return Electron_Microscope_Agent(llm_config)
