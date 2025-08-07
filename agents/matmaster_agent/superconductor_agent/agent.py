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
from agents.matmaster_agent.superconductor_agent.prompt import (
    SuperconductorAgentDescription,
    SuperconductorAgentInstruction,
    SuperconductorAgentName,
    SuperconductorResultAgentDescription,
    SuperconductorResultAgentName,
    SuperconductorResultCoreAgentInstruction,
    SuperconductorResultCoreAgentName,
    SuperconductorResultTransferAgentInstruction,
    SuperconductorResultTransferAgentName,
    SuperconductorSubmitAgentDescription,
    SuperconductorSubmitAgentName,
    SuperconductorSubmitCoreAgentDescription,
    SuperconductorSubmitCoreAgentInstruction,
    SuperconductorSubmitCoreAgentName,
    SuperconductorSubmitRenderAgentName,
    SuperconductorTransferAgentInstruction,
    SuperconductorTransferAgentName,
)

from .constant import SuperconductorServerUrl

SuperconductorBohriumExecutor = copy.deepcopy(BohriumExecutor)
SuperconductorBohriumStorge = copy.deepcopy(BohriumStorge)
SuperconductorBohriumExecutor["machine"]["remote_profile"][
    "image_address"] = "registry.dp.tech/dptech/dp/native/prod-435364/dpa-thermo-superconductor:2"

sse_params = SseServerParams(url=SuperconductorServerUrl)

toolset = CalculationMCPToolset(
    connection_params=sse_params,
    storage=SuperconductorBohriumStorge,
    executor=SuperconductorBohriumExecutor,
    async_mode=True,
    wait=False,
    logging_callback=matmodeler_logging_handler
)


class SuperconductorAgent(BaseAsyncJobAgent):
    def __init__(self, llm_config):
        super().__init__(
            model=llm_config.gpt_4o,
            mcp_tools=[toolset],
            agent_name=SuperconductorAgentName,
            agent_description=SuperconductorAgentDescription,
            agent_instruction=SuperconductorAgentInstruction,
            submit_core_agent_class=SubmitCoreCalculationMCPLlmAgent,
            submit_core_agent_name=SuperconductorSubmitCoreAgentName,
            submit_core_agent_description=SuperconductorSubmitCoreAgentDescription,
            submit_core_agent_instruction=SuperconductorSubmitCoreAgentInstruction,
            submit_render_agent_name=SuperconductorSubmitRenderAgentName,
            result_core_agent_class=ResultCalculationMCPLlmAgent,
            result_core_agent_name=SuperconductorResultCoreAgentName,
            result_core_agent_instruction=SuperconductorResultCoreAgentInstruction,
            result_transfer_agent_name=SuperconductorResultTransferAgentName,
            result_transfer_agent_instruction=SuperconductorResultTransferAgentInstruction,
            transfer_agent_name=SuperconductorTransferAgentName,
            transfer_agent_instruction=SuperconductorTransferAgentInstruction,
            submit_agent_name=SuperconductorSubmitAgentName,
            submit_agent_description=SuperconductorSubmitAgentDescription,
            result_agent_name=SuperconductorResultAgentName,
            result_agent_description=SuperconductorResultAgentDescription,
            dflow_flag=False,
            supervisor_agent=MATMASTER_AGENT_NAME
        )


def init_superconductor_agent(llm_config) -> BaseAgent:
    return SuperconductorAgent(llm_config)

