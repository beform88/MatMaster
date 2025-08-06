import os

from agents.matmaster_agent.base_agents.job_agent import (
    BaseAsyncJobAgent,
    ResultCalculationMCPLlmAgent,
    SubmitCoreCalculationMCPLlmAgent,
)
from agents.matmaster_agent.constant import (
    DPA_CALCULATIONS_AGENT_NAME,
    BohriumExecutor,
    BohriumStorge,
)
from agents.matmaster_agent.logger import matmodeler_logging_handler
from pathlib import Path
from typing import Any, Dict

from dp.agent.adapter.adk import CalculationMCPToolset
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools.mcp_tool.mcp_session_manager import SseServerParams
from google.genai import types


DPA_CALCULATOR_URL = "https://dpa-uuid1750659890.app-space.dplink.cc/sse?token=fa66cc76b6724d5590a89546772963fd"
mcp_tools_dpa = CalculationMCPToolset(
    connection_params=SseServerParams(url=DPA_CALCULATOR_URL),
    storage=BohriumStorge,
    executor=BohriumExecutor,
    async_mode=True,
    wait=False,
    executor_map={
        "build_bulk_structure": None,
        "build_molecule_structure": None,
        "build_surface_slab": None,
        "build_surface_adsorbate": None
    },
    logging_callback=matmodeler_logging_handler
)

class DPACalculationsAgent(BaseAsyncJobAgent):
    def __init__(self, llm_config):
        super().__init__(
            agent_name=DPA_CALCULATIONS_AGENT_NAME,
            mcp_tools=[mcp_tools_dpa],,
            llm_config=llm_config.gpt_4o,
            agent_description="An agent specialized in computational research using Deep Potential",
            agent_instruction=(
                "You are an expert in materials science and computational chemistry. "
                "Help users perform Deep Potential calculations including structure optimization, "
                "molecular dynamics and property calculations. "
                "Use default parameters if the users do not mention, but let users confirm them before submission. "
                "In multi-step workflows involving file outputs, always use the URI of the previous step's file "
                "as the input for the next tool. Always verify the input parameters to users and provide "
                "clear explanations of results."
            ),
            submit_core_agent_class=SubmitCoreCalculationMCPLlmAgent,
            result_core_agent_class=ResultCalculationMCPLlmAgent
        )

def init_dpa_calculations_agent() -> LlmAgent:
    dpa_agent = DPACalculationsAgent(MatMasterLlmConfig)  # Reuse existing config or create new one
    track_adk_agent_recursive(dpa_agent, MatMasterLlmConfig.opik_tracer)  # Add tracing
    
    return dpa_agent

# Replace the global instance
root_agent = init_dpa_calculations_agent()