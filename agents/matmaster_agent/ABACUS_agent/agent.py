from pathlib import Path
from dotenv import load_dotenv

from dp.agent.adapter.adk import CalculationMCPToolset
from google.adk.agents import LlmAgent, BaseAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.tools.mcp_tool.mcp_session_manager import SseServerParams

from agents.matmaster_agent import llm_config
from agents.matmaster_agent.llm_config import MatMasterLlmConfig
from agents.matmaster_agent.logger import matmodeler_logging_handler

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

from agents.matmaster_agent.ABACUS_agent.prompt import (
    ABACUS_AGENT_DESCRIPTION,
    ABACUS_AGENT_INSTRCUTION,
)

from agents.matmaster_agent.ABACUS_agent.constant import (
    ABACUS_CALCULATOR_AGENT_NAME,
    ABACUS_CALCULATOR_URL,
    EXECUTOR_MAP,
)

mcp_tools_abacus = CalculationMCPToolset(
    connection_params=SseServerParams(
        url=ABACUS_CALCULATOR_URL,
        sse_read_timeout = 3600,
    ),
    async_mode=True,
    wait=False,
    executor = BohriumExecutor,
    executor_map = EXECUTOR_MAP,
    storage = BohriumStorge,
    logging_callback=matmodeler_logging_handler
)

class ABACUSCalculatorAgent(LlmAgent):
    def __init__(self, llm_config):
        super().__init__(
            model=llm_config.deepseek_chat,
            name=ABACUS_CALCULATOR_AGENT_NAME,
            description=ABACUS_AGENT_DESCRIPTION,
            instruction=ABACUS_AGENT_INSTRCUTION,
            tools=[mcp_tools_abacus]
        )

def init_abacus_calculation_agent(llm_config):
    return ABACUSCalculatorAgent(llm_config)
