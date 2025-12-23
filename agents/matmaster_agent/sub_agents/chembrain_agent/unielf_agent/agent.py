from dp.agent.adapter.adk import CalculationMCPToolset
from google.adk.agents import BaseAgent
from google.adk.tools.mcp_tool.mcp_session_manager import (
    StreamableHTTPServerParams,
)

from agents.matmaster_agent.constant import BohriumStorge
from agents.matmaster_agent.core_agents.public_agents.sync_agent import (
    BaseSyncAgentWithToolValidator,
)
from agents.matmaster_agent.llm_config import MatMasterLlmConfig

from ..constant import CHEMBRAIN_AGENT_NAME
from .constant import UNIELF_SERVER_URL, UniELFAgentName
from .prompt import description, instruction_en

# Configure SSE params
sse_params = StreamableHTTPServerParams(url=UNIELF_SERVER_URL)
unielf_toolset = CalculationMCPToolset(
    connection_params=sse_params, storage=BohriumStorge
)


# Create agent
# def init_unielf_agent(llm_config):
#     selected_model = llm_config.gpt_4o
#     unielf_agent = BaseSyncAgent(
#         name=UniELFAgentName,
#         model=selected_model,
#         instruction=instruction_en,
#         description=description,
#         tools=[unielf_toolset],
#         supervisor_agent=CHEMBRAIN_AGENT_NAME,
#     )
#     return unielf_agent


class UniELFAgent(BaseSyncAgentWithToolValidator):
    def __init__(self, llm_config, name_suffix=''):
        selected_model = llm_config.default_litellm_model
        super().__init__(
            name=UniELFAgentName + name_suffix,
            model=selected_model,
            instruction=instruction_en,
            description=description,
            tools=[unielf_toolset],
            supervisor_agent=CHEMBRAIN_AGENT_NAME,
        )


def init_unielf_agent(llm_config) -> BaseAgent:
    return UniELFAgent(llm_config)


root_agent = init_unielf_agent(MatMasterLlmConfig)
