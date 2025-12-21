from dp.agent.adapter.adk import CalculationMCPToolset
from google.adk.agents import BaseAgent
from google.adk.tools.mcp_tool.mcp_session_manager import SseServerParams

from agents.matmaster_agent.constant import MATMASTER_AGENT_NAME
from agents.matmaster_agent.core_agents.worker_agents.sync_agent import (
    BaseSyncAgentWithToolValidator,
)
from agents.matmaster_agent.llm_config import LLMConfig
from agents.matmaster_agent.logger import matmodeler_logging_handler
from agents.matmaster_agent.sub_agents.XRD_agent.constant import (
    XRD_AGENT_NAME,
    XRD_BOHRIUM_STORAGE,
    XRD_MCP_SERVER_URL,
)
from agents.matmaster_agent.sub_agents.XRD_agent.prompt import (
    XRDAgentDescription,
    XRDAgentInstruction,
)

xrd_toolset = CalculationMCPToolset(
    connection_params=SseServerParams(url=XRD_MCP_SERVER_URL),
    storage=XRD_BOHRIUM_STORAGE,
    logging_callback=matmodeler_logging_handler,
)


class XRDAgent(BaseSyncAgentWithToolValidator):
    def __init__(self, llm_config: LLMConfig):
        super().__init__(
            model=llm_config.default_litellm_model,
            name=XRD_AGENT_NAME,
            description=XRDAgentDescription,
            instruction=XRDAgentInstruction,
            tools=[xrd_toolset],
            render_tool_response=True,
            supervisor_agent=MATMASTER_AGENT_NAME,
        )


def init_xrd_agent(llm_config) -> BaseAgent:
    return XRDAgent(llm_config)
