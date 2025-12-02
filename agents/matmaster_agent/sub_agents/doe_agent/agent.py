from dp.agent.adapter.adk import CalculationMCPToolset
from google.adk.agents import BaseAgent
from google.adk.tools.mcp_tool.mcp_session_manager import SseServerParams

from agents.matmaster_agent.constant import MATMASTER_AGENT_NAME
from agents.matmaster_agent.job_agents.agent import BaseAsyncJobAgent
from agents.matmaster_agent.llm_config import LLMConfig
from agents.matmaster_agent.logger import matmodeler_logging_handler
from agents.matmaster_agent.sub_agents.doe_agent.constant import (
    DOE_BOHRIUM_EXECUTOR,
    DOE_BOHRIUM_STORAGE,
    DOE_SERVER_URL,
)
from agents.matmaster_agent.sub_agents.doe_agent.prompt import (
    DoEAgentDescription,
    DoEAgentInstruction,
    DoEAgentName,
)

# Configure SSE params
doe_toolset = CalculationMCPToolset(
    connection_params=SseServerParams(url=DOE_SERVER_URL),
    storage=DOE_BOHRIUM_STORAGE,
    executor=DOE_BOHRIUM_EXECUTOR,
    async_mode=True,
    wait=False,
    logging_callback=matmodeler_logging_handler,
)


class DoEAgent(BaseAsyncJobAgent):
    def __init__(self, llm_config: LLMConfig):
        super().__init__(
            model=llm_config.default_litellm_model,
            tools=[doe_toolset],
            name=DoEAgentName,
            description=DoEAgentDescription,
            instruction=DoEAgentInstruction,
            dflow_flag=False,
            supervisor_agent=MATMASTER_AGENT_NAME,
        )


def init_doe_agent(llm_config) -> BaseAgent:
    return DoEAgent(llm_config)
