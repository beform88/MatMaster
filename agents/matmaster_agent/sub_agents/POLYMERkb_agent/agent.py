from dotenv import load_dotenv
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
from agents.matmaster_agent.llm_config import LLMConfig
from agents.matmaster_agent.sub_agents.POLYMERkb_agent.constant import (
    POLYMER_SERVER_URL,
)
from agents.matmaster_agent.sub_agents.POLYMERkb_agent.prompt import (
    POLYMERKbAgentDescription,
    POLYMERKbAgentInstruction,
    POLYMERKbAgentName,
)

load_dotenv()

# Initialize MCP tools for POLYMERkb Knowledge Base
polymer_kb_toolset = CalculationMCPToolset(
    connection_params=SseServerParams(url=POLYMER_SERVER_URL),
    storage=BohriumStorge,
    executor=LOCAL_EXECUTOR,
)


class POLYMERKbAgent(BaseSyncAgentWithToolValidator):
    def __init__(self, llm_config: LLMConfig, name_suffix=''):
        super().__init__(
            model=llm_config.default_litellm_model,
            doc_summary=True,
            name=POLYMERKbAgentName + name_suffix,
            description=POLYMERKbAgentDescription,
            instruction=POLYMERKbAgentInstruction,
            tools=[polymer_kb_toolset],
            render_tool_response=False,
            supervisor_agent=MATMASTER_AGENT_NAME,
        )


def init_polymer_kb_agent(llm_config: LLMConfig, name_suffix='') -> BaseAgent:
    return POLYMERKbAgent(llm_config, name_suffix)
