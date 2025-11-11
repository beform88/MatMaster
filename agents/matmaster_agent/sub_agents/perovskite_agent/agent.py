import dotenv
from dp.agent.adapter.adk import CalculationMCPToolset
from google.adk.agents import BaseAgent
from google.adk.tools.mcp_tool.mcp_session_manager import SseServerParams

from agents.matmaster_agent.base_agents.public_agent import (
    BaseSyncAgentWithToolValidator,
)
from agents.matmaster_agent.constant import (
    LOCAL_EXECUTOR,
    MATMASTER_AGENT_NAME,
    BohriumStorge,
)

from .constant import PEROVSKITE_PLOT_URL, PerovskiteAgentName
from .prompt import PerovskiteAgentDescription, PerovskiteAgentInstruction

dotenv.load_dotenv()

# Initialize MCP tools and agent
perovskite_toolset = CalculationMCPToolset(
    connection_params=SseServerParams(url=PEROVSKITE_PLOT_URL),
    storage=BohriumStorge,
    executor=LOCAL_EXECUTOR,
)


class Perovskite_Agent(BaseSyncAgentWithToolValidator):
    def __init__(self, llm_config):
        super().__init__(
            model=llm_config.gpt_5_chat,
            name=PerovskiteAgentName,
            description=PerovskiteAgentDescription,
            instruction=PerovskiteAgentInstruction,
            tools=[perovskite_toolset],
            render_tool_response=True,
            supervisor_agent=MATMASTER_AGENT_NAME,
        )


def init_perovskite_agent(llm_config) -> BaseAgent:
    return Perovskite_Agent(llm_config)
