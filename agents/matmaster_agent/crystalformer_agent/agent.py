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
from agents.matmaster_agent.crystalformer_agent.prompt import (
    CrystalformerAgentDescription,
    CrystalformerAgentInstruction,
    CrystalformerAgentName,
    CrystalformerResultAgentDescription,
    CrystalformerResultAgentName,
    CrystalformerResultCoreAgentInstruction,
    CrystalformerResultCoreAgentName,
    CrystalformerResultTransferAgentInstruction,
    CrystalformerResultTransferAgentName,
    CrystalformerSubmitAgentDescription,
    CrystalformerSubmitAgentName,
    CrystalformerSubmitCoreAgentDescription,
    CrystalformerSubmitCoreAgentInstruction,
    CrystalformerSubmitCoreAgentName,
    CrystalformerSubmitRenderAgentName,
    CrystalformerTransferAgentInstruction,
    CrystalformerTransferAgentName,
)

from .constant import CrystalformerServerUrl

CrystalformerBohriumExecutor = copy.deepcopy(BohriumExecutor)
CrystalformerBohriumStorge = copy.deepcopy(BohriumStorge)
CrystalformerBohriumExecutor["machine"]["remote_profile"]["image_address"] = "registry.dp.tech/dptech/dp/native/prod-788025/crystalformer:t4"
CrystalformerBohriumExecutor["machine"]["remote_profile"]["machine_type"] = "c8_m31_1 * NVIDIA T4"

sse_params = SseServerParams(url=CrystalformerServerUrl)

toolset = CalculationMCPToolset(
    connection_params=sse_params,
    storage=CrystalformerBohriumStorge,
    executor=CrystalformerBohriumExecutor,
    async_mode=True,
    wait=False,
    logging_callback=matmodeler_logging_handler
)


class CrystalformerAgent(BaseAsyncJobAgent):
    def __init__(self, llm_config):
        super().__init__(
            model=llm_config.gpt_4o,
            mcp_tools=[toolset],
            agent_name=CrystalformerAgentName,
            agent_description=CrystalformerAgentDescription,
            agent_instruction=CrystalformerAgentInstruction,
            submit_core_agent_description=CrystalformerSubmitCoreAgentDescription,
            submit_core_agent_instruction=CrystalformerSubmitCoreAgentInstruction,
            result_core_agent_instruction=CrystalformerResultCoreAgentInstruction,
            result_transfer_agent_instruction=CrystalformerResultTransferAgentInstruction,
            transfer_agent_instruction=CrystalformerTransferAgentInstruction,
            submit_agent_description=CrystalformerSubmitAgentDescription,
            result_agent_description=CrystalformerResultAgentDescription,
            dflow_flag=False,
            supervisor_agent=MATMASTER_AGENT_NAME
        )


def init_crystalformer_agent(llm_config) -> BaseAgent:
    return CrystalformerAgent(llm_config)