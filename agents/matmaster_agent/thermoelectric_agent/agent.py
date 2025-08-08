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
ThermoelectricBohriumExecutor["machine"]["remote_profile"][
    "image_address"] = "registry.dp.tech/dptech/dp/native/prod-435364/dpa-thermo-superconductor:1"

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
            submit_core_agent_description=ThermoSubmitCoreAgentDescription,
            submit_core_agent_instruction=ThermoSubmitCoreAgentInstruction,
            result_core_agent_instruction=ThermoResultCoreAgentInstruction,
            result_transfer_agent_instruction=ThermoResultTransferAgentInstruction,
            transfer_agent_instruction=ThermoTransferAgentInstruction,
            submit_agent_description=ThermoSubmitAgentDescription,
            result_agent_description=ThermoResultAgentDescription,
            dflow_flag=False,
            supervisor_agent=MATMASTER_AGENT_NAME
        )


def init_thermoelectric_agent(llm_config) -> BaseAgent:
    return ThermoAgent(llm_config)

# Replace the global instance
# root_agent = init_thermoelectric_agent()

# import os
# from agents.matmaster_agent.base_agents.job_agent import (
#    BaseAsyncJobAgent,
#    ResultCalculationMCPLlmAgent,
#    SubmitCoreCalculationMCPLlmAgent,
# )
# from agents.matmaster_agent.constant import (
#    THERMOELECTRIC_AGENT_NAME,
#    BohriumExecutor,
#    BohriumStorge,
# )
# from agents.matmaster_agent.logger import matmodeler_logging_handler
#
# from dp.agent.adapter.adk import CalculationMCPToolset
# from google.adk.agents import LlmAgent
# from google.adk.models.lite_llm import LiteLlm
# from google.adk.sessions import InMemorySessionService
# from google.adk.tools.mcp_tool.mcp_session_manager import SseServerParams


### === MCP toolset ===
# mcp_tools_thermoelectric = CalculationMCPToolset(
#    connection_params=SseServerParams(url=THERMOELECTRIC_TOOL_URL),
#    storage=BohriumStorge,
#    executor=BohriumExecutor,
#    async_mode=True,
#    wait=False,
#    logging_callback=matmodeler_logging_handler
# )
#
# class ThermoelectricAgent(BaseAsyncJobAgent):
#    def __init__(self, llm_config):
#        super().__init__(
#          agent_name=THERMOELECTRIC_AGENT_NAME,
#          mcp_tools=[mcp_tools_thermoelectric],
#          llm_config=llm_config.gpt_4o,
#          agent_description="Helps with Deep Potential calculations and material thermoelectronic properties.",
#          agent_instruction=(
#                  "You are an expert in thermoelectric materials. "
#                  "Help users evaluate thermoelectric properties, including HSE functional "
#                  "bandgap, shear modulus, bulk modulus, n-type and p-type power factors, "
#                  "n-type and p-type carrier mobility, and Seebeck coefficient. "
#                  "Please use default settings if not specified, but always confirm with the user before submission."
#          ),
#          submit_core_agent_class=SubmitCoreCalculationMCPLlmAgent, 
#          result_core_agent_class=ResultCalculationMCPLlmAgent
#        )
#    def init_thermoelectric_agent() -> LlmAgent:
#       thermoelectric_agent = ThermoelectricAgent(MatMasterLlmConfig)  # Reuse existing config or create new one
#       track_adk_agent_recursive(thermoelectric_agent, MatMasterLlmConfig.opik_tracer)  # Add tracing
#
#       return thermoelectric_agent
#
## Replace the global instance
# root_agent = init_thermoelectric_agent()
