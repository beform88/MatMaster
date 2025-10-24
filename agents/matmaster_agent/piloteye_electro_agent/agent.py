from dp.agent.adapter.adk import CalculationMCPToolset
from google.adk.agents import BaseAgent
from google.adk.tools.mcp_tool.mcp_session_manager import SseServerParams

from agents.matmaster_agent.base_agents.multi_agent import BaseAsyncJobAgent
from agents.matmaster_agent.constant import MATMASTER_AGENT_NAME
from agents.matmaster_agent.logger import matmodeler_logging_handler
from agents.matmaster_agent.piloteye_electro_agent.constant import (
    PILOTEYE_BOHRIUM_EXECUTOR,
    PILOTEYE_BOHRIUM_STORAGE,
    PILOTEYE_SERVER_URL,
)
from agents.matmaster_agent.piloteye_electro_agent.prompt import (
    PiloteyeElectroAgentDescription,
    PiloteyeElectroAgentInstruction,
    PiloteyeElectroAgentName,
)

# Configure SSE params
piloteye_electro_tool = CalculationMCPToolset(
    connection_params=SseServerParams(url=PILOTEYE_SERVER_URL),
    storage=PILOTEYE_BOHRIUM_STORAGE,
    executor=PILOTEYE_BOHRIUM_EXECUTOR,
    async_mode=True,
    wait=False,
    logging_callback=matmodeler_logging_handler,
)


# # Create agent
# def init_unielf_agent(llm_config):
#     selected_model = llm_config.gpt_4o
#     unielf_agent = CalculationLlmAgent(
#         name=UniELFAgentName,
#         model=selected_model,
#         instruction=instruction_en,
#         description=description,
#         tools=[toolset]
#     )
#     return unielf_agent


# root_agent = init_unielf_agent(ChemBrainLlmConfig)


class PiloteyeElectroAgent(BaseAsyncJobAgent):
    def __init__(self, llm_config):
        super().__init__(
            model=llm_config.gpt_5_chat,
            mcp_tools=[piloteye_electro_tool],
            agent_name=PiloteyeElectroAgentName,
            agent_description=PiloteyeElectroAgentDescription,
            agent_instruction=PiloteyeElectroAgentInstruction,
            dflow_flag=False,
            supervisor_agent=MATMASTER_AGENT_NAME,
        )


def init_piloteye_electro_agent(llm_config) -> BaseAgent:
    return PiloteyeElectroAgent(llm_config)
