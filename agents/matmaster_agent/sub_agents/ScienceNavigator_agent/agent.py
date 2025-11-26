from google.adk.tools.mcp_tool import McpToolset
from google.adk.agents import BaseAgent
from google.adk.tools.mcp_tool.mcp_session_manager import (
    SseServerParams,
)

from agents.matmaster_agent.constant import MATMASTER_AGENT_NAME
from agents.matmaster_agent.base_agents.public_agent import (
    BaseSyncAgentWithToolValidator,
)
from agents.matmaster_agent.llm_config import LLMConfig
from agents.matmaster_agent.sub_agents.ScienceNavigator_agent.constant import (
    SCIENCE_NAVIGATOR_AGENT_NAME,
    SCIENCE_NAVIGATOR_MCP_SERVER_URL,
)
from agents.matmaster_agent.sub_agents.ScienceNavigator_agent.prompt import (
    SCIENCE_NAVIGATOR_AGENT_DESCRIPTION,
    SCIENCE_NAVIGATOR_AGENT_INSTRUCTION,
)

science_navigator_toolset = McpToolset(
    connection_params=SseServerParams(url=SCIENCE_NAVIGATOR_MCP_SERVER_URL)
)


class ScienceNavigatorAgent(BaseSyncAgentWithToolValidator):
    def __init__(self, llm_config: LLMConfig):
        super().__init__(
            name=SCIENCE_NAVIGATOR_AGENT_NAME,
            tools=[science_navigator_toolset],
            model=llm_config.default_litellm_model,
            description=SCIENCE_NAVIGATOR_AGENT_DESCRIPTION,
            instruction=SCIENCE_NAVIGATOR_AGENT_INSTRUCTION,
            supervisor_agent=MATMASTER_AGENT_NAME,
            render_tool_response=True,
        )


def init_science_navigator_agent(llm_config) -> BaseAgent:
    return ScienceNavigatorAgent(llm_config)
