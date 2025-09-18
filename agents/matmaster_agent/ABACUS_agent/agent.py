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
    LOCAL_EXECUTOR
)

from agents.matmaster_agent.ABACUS_agent.prompt import (
    ABACUS_AGENT_NAME,
    ABACUS_AGENT_DESCRIPTION,
    ABACUS_AGENT_INSTRUCTION,
    ABACUS_SUBMIT_CORE_AGENT_NAME,
    ABACUS_SUBMIT_CORE_AGENT_DESCRIPTION,
    ABACUS_SUBMIT_CORE_AGENT_INSTRUCTION,
    ABACUS_SUBMIT_RENDER_AGENT_NAME,
    ABACUS_RESULT_CORE_AGENT_NAME,
    ABACUS_RESULT_CORE_AGENT_INSTRUCTION,
    ABACUS_RESULT_TRANSFER_AGENT_NAME,
    ABACUS_RESULT_TRANSFER_AGENT_INSTRUCTION,
    ABACUS_TRANSFER_AGENT_NAME,
    ABACUS_TRANSFER_AGENT_INSTRCUTION,
    ABACUS_SUBMIT_AGENT_NAME,
    ABACUS_SUBMIT_AGENT_DESCRIPTION,
    ABACUS_RESULT_AGENT_NAME,
    ABACUS_RESULT_AGENT_DESCRIPTION
)

from agents.matmaster_agent.ABACUS_agent.constant import (
    ABACUS_CALCULATOR_URL,
    ABACUS_CALCULATOR_BOHRIUM_EXECUTOR,
    ABACUS_CALCULATOR_BOHRIUM_STORAGE,
)

mcp_tools_abacus = CalculationMCPToolset(
    connection_params=SseServerParams(
        url=ABACUS_CALCULATOR_URL,
        sse_read_timeout = 3600,
    ),
    executor = ABACUS_CALCULATOR_BOHRIUM_EXECUTOR,
    storage = ABACUS_CALCULATOR_BOHRIUM_STORAGE,
    async_mode=True,
    wait=False,
    logging_callback=matmodeler_logging_handler
)

class ABACUSCalculatorAgent(BaseAsyncJobAgent):
    def __init__(self, llm_config):
        super().__init__(
            model=llm_config.gpt_5_chat,
            mcp_tools=[mcp_tools_abacus],
            agent_name=ABACUS_AGENT_NAME,
            agent_description=ABACUS_AGENT_DESCRIPTION,
            agent_instruction=ABACUS_AGENT_INSTRUCTION,
            dflow_flag=False,
            supervisor_agent=MATMASTER_AGENT_NAME,
            sync_tools=['abacus_prepare',
                        'abacus_modify_input',
                        'abacus_modify_stru',
                        'abacus_collect_data']
        )

def init_abacus_calculation_agent(llm_config) -> BaseAgent:
    return ABACUSCalculatorAgent(llm_config)