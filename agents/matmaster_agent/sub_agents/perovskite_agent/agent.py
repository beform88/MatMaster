import dotenv
from dp.agent.adapter.adk import CalculationMCPToolset
from google.adk.agents import BaseAgent
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPServerParams

from agents.matmaster_agent.constant import (
    LOCAL_EXECUTOR,
    MATMASTER_AGENT_NAME,
    BohriumStorge,
)

from ...core_agents.worker_agents.sync_agent import BaseSyncAgentWithToolValidator
from ...llm_config import LLMConfig
from .constant import PEROVSKITE_RESEARCH_URL, UNIMOL_SERVER_URL, PerovskiteAgentName
from .prompt import PerovskiteAgentDescription, PerovskiteAgentInstruction

dotenv.load_dotenv()

# Initialize MCP tools and agent
perovskite_toolset = CalculationMCPToolset(
    connection_params=StreamableHTTPServerParams(url=PEROVSKITE_RESEARCH_URL),
    storage=BohriumStorge,
    executor=LOCAL_EXECUTOR,
)
unimol_toolset = CalculationMCPToolset(
    connection_params=StreamableHTTPServerParams(url=UNIMOL_SERVER_URL),
    storage=BohriumStorge,
    executor=LOCAL_EXECUTOR,
)


class PerovskiteAgent(BaseSyncAgentWithToolValidator):
    def __init__(self, llm_config):
        super().__init__(
            model=llm_config.default_litellm_model,
            name=PerovskiteAgentName,
            description=PerovskiteAgentDescription,
            instruction=PerovskiteAgentInstruction,
            tools=[perovskite_toolset, unimol_toolset],
            render_tool_response=True,
            supervisor_agent=MATMASTER_AGENT_NAME,
        )


def init_perovskite_agent(llm_config: LLMConfig) -> BaseAgent:
    return PerovskiteAgent(llm_config)
