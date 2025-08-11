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
from agents.matmaster_agent.thermoelectric_agent.prompt import (
    ThermoAgentDescription,
    ThermoAgentInstruction,
    ThermoAgentName,
    ThermoResultAgentDescription,
    ThermoResultAgentName,
    ThermoResultCoreAgentInstruction,
    ThermoResultCoreAgentName,
    ThermoResultTransferAgentInstruction,
    ThermoResultTransferAgentName,
    ThermoSubmitAgentDescription,
    ThermoSubmitAgentName,
    ThermoSubmitCoreAgentDescription,
    ThermoSubmitCoreAgentInstruction,
    ThermoSubmitCoreAgentName,
    ThermoSubmitRenderAgentName,
    ThermoTransferAgentInstruction,
    ThermoTransferAgentName,
)

from .constant import ThermoelectricServerUrl

ThermoelectricBohriumExecutor = copy.deepcopy(BohriumExecutor)
ThermoelectricBohriumStorge = copy.deepcopy(BohriumStorge)
ThermoelectricBohriumExecutor["machine"]["remote_profile"]["image_address"] = "registry.dp.tech/dptech/dp/native/prod-435364/dpa-thermo-superconductor:6"

sse_params = SseServerParams(url=ThermoelectricServerUrl)

toolset = CalculationMCPToolset(
        connection_params=sse_params,
        storage=ThermoelectricBohriumStorge,
        executor=ThermoelectricBohriumExecutor,
        async_mode=True,
        wait=False,
        logging_callback=matmodeler_logging_handler
)

class ThermoAgent(BaseAsyncJobAgent):
    def __init__(self, llm_config):
        super().__init__(
          model=llm_config.gpt_4o,
          mcp_tools=[toolset],
          agent_name=ThermoAgentName,
          agent_description=ThermoAgentDescription,
          agent_instruction=ThermoAgentInstruction,
          submit_core_agent_class=SubmitCoreCalculationMCPLlmAgent,
          submit_core_agent_name=ThermoSubmitCoreAgentName,
          submit_core_agent_description=ThermoSubmitCoreAgentDescription,
          submit_core_agent_instruction=ThermoSubmitCoreAgentInstruction,
          submit_render_agent_name=ThermoSubmitRenderAgentName,
          result_core_agent_class=ResultCalculationMCPLlmAgent,
          result_core_agent_name=ThermoResultCoreAgentName,
          result_core_agent_instruction=ThermoResultCoreAgentInstruction,
          result_transfer_agent_name=ThermoResultTransferAgentName,
          result_transfer_agent_instruction=ThermoResultTransferAgentInstruction,
          transfer_agent_name=ThermoTransferAgentName,
          transfer_agent_instruction=ThermoTransferAgentInstruction,
          submit_agent_name=ThermoSubmitAgentName,
          submit_agent_description=ThermoSubmitAgentDescription,
          result_agent_name=ThermoResultAgentName,
          result_agent_description=ThermoResultAgentDescription,
          dflow_flag=False,
          supervisor_agent=MATMASTER_AGENT_NAME
        )

def init_thermoelectric_agent(llm_config) -> BaseAgent:
    return ThermoAgent(llm_config)

