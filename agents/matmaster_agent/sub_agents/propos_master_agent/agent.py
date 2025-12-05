from dp.agent.adapter.adk import CalculationMCPToolset
from google.adk.agents import BaseAgent
from google.adk.tools.mcp_tool.mcp_session_manager import (
    SseServerParams,
)

from agents.matmaster_agent.base_agents.public_agent import (
    BaseSyncAgentWithToolValidator,
)
from agents.matmaster_agent.constant import MATMASTER_AGENT_NAME
from agents.matmaster_agent.llm_config import LLMConfig
from agents.matmaster_agent.sub_agents.propos_master_agent.callback import (
    after_tool_callback,
    before_tool_callback,
)
from agents.matmaster_agent.sub_agents.propos_master_agent.constant import (
    PROPOSMATER_AGENT_NAME,
    PROPOSMATER_BOHRIUM_EXECUTOR,
    PROPOSMATER_BOHRIUM_STORAGE,
    PROPOSMATER_MCP_SERVER_URL,
)
from agents.matmaster_agent.sub_agents.propos_master_agent.prompt import (
    PROPOSMATER_DESCRIPTION,
    PROPOSMATER_INSTRUCTION,
)

proposmaster_toolset = CalculationMCPToolset(
    connection_params=SseServerParams(
        url=PROPOSMATER_MCP_SERVER_URL,
        timeout=360,
        sse_read_timeout=3600,
    ),
    executor=PROPOSMATER_BOHRIUM_EXECUTOR,
    storage=PROPOSMATER_BOHRIUM_STORAGE,
    async_mode=False,
    wait=False,
)


class ProposMasterAgent(BaseSyncAgentWithToolValidator):
    def __init__(self, llm_config: LLMConfig):
        super().__init__(
            name=PROPOSMATER_AGENT_NAME,
            tools=[proposmaster_toolset],
            model=llm_config.default_litellm_model,
            doc_summary=False,
            description=PROPOSMATER_DESCRIPTION,
            instruction=PROPOSMATER_INSTRUCTION,
            supervisor_agent=MATMASTER_AGENT_NAME,
            after_tool_callback=after_tool_callback,
            before_tool_callback=before_tool_callback,
            render_tool_response=False,
        )


def init_proposmaster_agent(llm_config) -> BaseAgent:
    return ProposMasterAgent(llm_config)
