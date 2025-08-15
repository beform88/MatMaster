from dp.agent.adapter.adk import CalculationMCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import SseServerParams

from agents.matmaster_agent.base_agents.job_agent import (
    CalculationMCPLlmAgent,
)
from agents.matmaster_agent.constant import BohriumStorge

from .constant import PEROVSKITE_PLOT_URL, PerovskiteAgentName
from .prompt import (
    PerovskiteAgentDescription,
    PerovskiteAgentInstruction,
)

import logging

logging.basicConfig(level=logging.INFO)


logging.info(f"Perovskite Agent URL: {PEROVSKITE_PLOT_URL}")
import dotenv
dotenv.load_dotenv()
import os
logging.info(f"Environment name: {os.getenv('OPIK_PROJECT_NAME')}")
BOHRIUM_PROJECT_ID = os.getenv('BOHRIUM_PROJECT_ID')
logging.info(f"Bohrium Project ID: {BOHRIUM_PROJECT_ID}")

print(f"Perovskite Agent URL: {PEROVSKITE_PLOT_URL}")
print(f"Environment name: {os.getenv('OPIK_PROJECT_NAME')}")
print(f"Bohrium Project ID: {BOHRIUM_PROJECT_ID}")

perovskite_toolset = CalculationMCPToolset(
    connection_params=SseServerParams(url=PEROVSKITE_PLOT_URL),
    storage=BohriumStorge,
)

def init_perovskite_agent(llm_config):
    """Initialize Perovskite Solar Cell Data Analysis Agent using CalculationMCPLlmAgent."""
    # Choose model per flag with sensible fallbacks
    model = llm_config.gpt_4o

    return CalculationMCPLlmAgent(
        model=model,
        name=PerovskiteAgentName,
        description=PerovskiteAgentDescription,
        instruction=PerovskiteAgentInstruction,
        tools=[perovskite_toolset],
    )


