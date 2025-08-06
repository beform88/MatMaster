import copy

from dp.agent.adapter.adk import CalculationMCPToolset
from google.adk.agents import BaseAgent
from google.adk.tools.mcp_tool.mcp_session_manager import SseServerParams

from agents.matmaster_agent.base_agents.job_agent import (
    BaseAsyncJobAgent,
    ResultCalculationMCPLlmAgent,
    SubmitCoreCalculationMCPLlmAgent,
)
from agents.matmaster_agent.constant import (
    MATMASTER_AGENT_NAME,
    BohriumExecutor,
    BohriumStorge,
)
from agents.matmaster_agent.logger import matmodeler_logging_handler
from agents.matmaster_agent.piloteye_electro_agent.prompt import (
    DPAAgentDescription,
    DPAAgentInstruction,
    DPAAgentName,
    DPAResultAgentDescription,
    DPAResultAgentName,
    DPAResultCoreAgentInstruction,
    DPAResultCoreAgentName,
    DPAResultTransferAgentInstruction,
    DPAResultTransferAgentName,
    DPASubmitAgentDescription,
    DPASubmitAgentName,
    DPASubmitCoreAgentDescription,
    DPASubmitCoreAgentInstruction,
    DPASubmitCoreAgentName,
    DPASubmitRenderAgentName,
    DPATransferAgentInstruction,
    DPATransferAgentName,
)

from .constant import UniELFServerUrl

UniELFBohriumExecutor = copy.deepcopy(BohriumExecutor)
UniELFBohriumExecutor["machine"]["remote_profile"]["image_address"] = "registry.dp.tech/dptech/unielf:v1.15.1"

# Configure SSE params
sse_params = SseServerParams(url=UniELFServerUrl)
toolset = CalculationMCPToolset(
    connection_params=sse_params,
    storage=BohriumStorge,
    executor=BohriumExecutor,
    async_mode=True,
    wait=False,
    logging_callback=matmodeler_logging_handler
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



class DPAAgent(BaseAsyncJobAgent):
    def __init__(self, llm_config):
        super().__init__(
            llm_config=llm_config,
            mcp_tools=[toolset],
            agent_name=DPAAgentName,
            agent_description=DPAAgentDescription,
            agent_instruction=DPAAgentInstruction,
            submit_core_agent_class=SubmitCoreCalculationMCPLlmAgent,
            submit_core_agent_name=DPASubmitCoreAgentName,
            submit_core_agent_description=DPASubmitCoreAgentDescription,
            submit_core_agent_instruction=DPASubmitCoreAgentInstruction,
            submit_render_agent_name=DPASubmitRenderAgentName,
            result_core_agent_class=ResultCalculationMCPLlmAgent,
            result_core_agent_name=DPAResultCoreAgentName,
            result_core_agent_instruction=DPAResultCoreAgentInstruction,
            result_transfer_agent_name=DPAResultTransferAgentName,
            result_transfer_agent_instruction=DPAResultTransferAgentInstruction,
            transfer_agent_name=DPATransferAgentName,
            transfer_agent_instruction=DPATransferAgentInstruction,
            submit_agent_name=DPASubmitAgentName,
            submit_agent_description=DPASubmitAgentDescription,
            result_agent_name=DPAResultAgentName,
            result_agent_description=DPAResultAgentDescription,
            dflow_flag=False,
            supervisor_agent=MATMASTER_AGENT_NAME
        )


def init_piloteye_electro_agent(llm_config) -> BaseAgent:
    return DPAAgent(llm_config)
