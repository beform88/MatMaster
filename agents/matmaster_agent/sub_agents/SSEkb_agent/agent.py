from dotenv import load_dotenv
from dp.agent.adapter.adk import CalculationMCPToolset
from google.adk.agents import BaseAgent
from google.adk.tools.mcp_tool.mcp_session_manager import SseServerParams

from agents.matmaster_agent.constant import (
    LOCAL_EXECUTOR,
    MATMASTER_AGENT_NAME,
    BohriumStorge,
)
from agents.matmaster_agent.core_agents.public_agents.sync_agent import (
    BaseSyncAgentWithToolValidator,
)
from agents.matmaster_agent.llm_config import LLMConfig
from agents.matmaster_agent.sub_agents.SSEkb_agent.constant import (
    SSE_SERVER_URL,
)
from agents.matmaster_agent.sub_agents.SSEkb_agent.prompt import SSEKbAgentName

load_dotenv()

# Initialize MCP tools for SSEkb Knowledge Base
sse_kb_toolset = CalculationMCPToolset(
    connection_params=SseServerParams(url=SSE_SERVER_URL),
    storage=BohriumStorge,
    executor=LOCAL_EXECUTOR,
)


class SSEKbAgent(BaseSyncAgentWithToolValidator):
    def __init__(self, llm_config: LLMConfig, name_suffix=''):
        super().__init__(
            model=llm_config.default_litellm_model,
            doc_summary=True,
            name=SSEKbAgentName + name_suffix,
            description='',
            instruction='',
            tools=[sse_kb_toolset],
            render_tool_response=False,
            supervisor_agent=MATMASTER_AGENT_NAME,
        )


def init_sse_kb_agent(llm_config: LLMConfig, name_suffix='') -> BaseAgent:
    return SSEKbAgent(llm_config, name_suffix)
