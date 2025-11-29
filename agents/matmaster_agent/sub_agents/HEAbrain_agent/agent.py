from dotenv import load_dotenv
from dp.agent.adapter.adk import CalculationMCPToolset
from google.adk.agents import BaseAgent
from google.adk.tools.mcp_tool.mcp_session_manager import SseServerParams

from agents.matmaster_agent.base_agents.public_agent import (
    BaseSyncAgentWithToolValidator,
)
from agents.matmaster_agent.constant import LOCAL_EXECUTOR, BohriumStorge, MATMASTER_AGENT_NAME
from agents.matmaster_agent.llm_config import LLMConfig
from agents.matmaster_agent.sub_agents.HEAbrain_agent.constant import (
    HEA_BRAIN_AGENT_NAME,
    HEA_SERVER_URL,
)
from agents.matmaster_agent.sub_agents.HEAbrain_agent.prompt import (
    HEABrainAgentDescription,
    HEABrainAgentInstruction,
    HEABrainAgentName,
)

load_dotenv()

# Initialize MCP tools for HEA Knowledge Base
hea_brain_toolset = CalculationMCPToolset(
    connection_params=SseServerParams(url=HEA_SERVER_URL),
    storage=BohriumStorge,
    executor=LOCAL_EXECUTOR,
)


class HEABrainAgent(BaseSyncAgentWithToolValidator):
    def __init__(self, llm_config: LLMConfig, name_suffix=''):
        super().__init__(
            model=llm_config.default_litellm_model,
            name=HEABrainAgentName + name_suffix,
            description=HEABrainAgentDescription,
            instruction=HEABrainAgentInstruction,
            tools=[hea_brain_toolset],
            render_tool_response=True,
            supervisor_agent=MATMASTER_AGENT_NAME,
        )


def init_hea_brain_agent(llm_config: LLMConfig, name_suffix='') -> BaseAgent:
    return HEABrainAgent(llm_config, name_suffix)
