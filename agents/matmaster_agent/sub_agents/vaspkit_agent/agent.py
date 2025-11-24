from dp.agent.adapter.adk import CalculationMCPToolset
from google.adk.agents import BaseAgent
from google.adk.tools.mcp_tool.mcp_session_manager import SseServerParams

from agents.matmaster_agent.constant import MATMASTER_AGENT_NAME
from agents.matmaster_agent.job_agents.agent import BaseAsyncJobAgent
from agents.matmaster_agent.llm_config import LLMConfig
from agents.matmaster_agent.logger import matmodeler_logging_handler
from agents.matmaster_agent.sub_agents.vaspkit_agent.constant import (
    VASPKIT_AGENT_NAME,
    VASPKIT_BOHRIUM_EXECUTOR,
    VASPKIT_BOHRIUM_STORAGE,
    VASPKIT_MCP_SERVER_URL,
)
from agents.matmaster_agent.sub_agents.vaspkit_agent.finance import vaspkit_cost_func
from agents.matmaster_agent.sub_agents.vaspkit_agent.prompt import (
    VASPKITAgentDescription,
    VASPKITAgentInstruction,
)

vaspkit_toolset = CalculationMCPToolset(
    connection_params=SseServerParams(url=VASPKIT_MCP_SERVER_URL),
    storage=VASPKIT_BOHRIUM_STORAGE,
    executor=VASPKIT_BOHRIUM_EXECUTOR,
    async_mode=True,
    wait=False,
    logging_callback=matmodeler_logging_handler,
)


class VASPKITAgent(BaseAsyncJobAgent):
    def __init__(self, llm_config: LLMConfig):
        super().__init__(
            name=VASPKIT_AGENT_NAME,
            tools=[vaspkit_toolset],
            model=llm_config.default_litellm_model,
            description=VASPKITAgentDescription,
            instruction=VASPKITAgentInstruction,
            dflow_flag=False,
            supervisor_agent=MATMASTER_AGENT_NAME,
            cost_func=vaspkit_cost_func,
        )


def init_vaspkit_agent(llm_config) -> BaseAgent:
    return VASPKITAgent(llm_config)
