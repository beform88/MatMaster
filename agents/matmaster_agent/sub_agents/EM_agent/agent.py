from dp.agent.adapter.adk import CalculationMCPToolset
from google.adk.agents import BaseAgent
from google.adk.tools.mcp_tool.mcp_session_manager import SseServerParams

from agents.matmaster_agent.base_agents.public_agent import (
    BaseSyncAgentWithToolValidator,
)
from agents.matmaster_agent.constant import MATMASTER_AGENT_NAME
from agents.matmaster_agent.llm_config import LLMConfig
from agents.matmaster_agent.logger import matmodeler_logging_handler
from agents.matmaster_agent.sub_agents.EM_agent.constant import (
    EM_AGENT_NAME,
    EM_BOHRIUM_STORAGE,
    EM_MCP_SERVER_URL,
)
from agents.matmaster_agent.sub_agents.EM_agent.prompt import (
    EMAgentDescription,
    EMAgentInstruction,
)

em_toolset = CalculationMCPToolset(
    connection_params=SseServerParams(url=EM_MCP_SERVER_URL),
    storage=EM_BOHRIUM_STORAGE,
    logging_callback=matmodeler_logging_handler,
)


class EMAgent(BaseSyncAgentWithToolValidator):
    def __init__(self, llm_config: LLMConfig):
        super().__init__(
            model=llm_config.default_litellm_model,
            name=EM_AGENT_NAME,
            description=EMAgentDescription,
            instruction=EMAgentInstruction,
            tools=[em_toolset],
            render_tool_response=True,
            supervisor_agent=MATMASTER_AGENT_NAME,
        )


def init_em_agent(llm_config) -> BaseAgent:
    return EMAgent(llm_config)
