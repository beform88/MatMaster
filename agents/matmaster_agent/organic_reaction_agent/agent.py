import os
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import SseServerParams
from agents.matmaster_agent.llm_config import MatMasterLlmConfig

from dp.agent.adapter.adk import CalculationMCPToolset

from agents.matmaster_agent.organic_reaction_agent.constant import (
    ORGANIC_REACTION_BOHRIUM_EXECUTOR,
    ORGANIC_REACTION_BOHRIUM_STORAGE,
    ORGANIC_REACTION_SERVER_URL,
    ORGANIC_REACTION_AGENT_NAME,
)
from agents.matmaster_agent.organic_reaction_agent.prompt import (
    description,
    instruction_en,
)

from agents.matmaster_agent.base_agents.job_agent import (
    CalculationMCPLlmAgent,
    BaseAsyncJobAgent,
    ResultCalculationMCPLlmAgent,
    SubmitCoreCalculationMCPLlmAgent,
)
from agents.matmaster_agent.constant import (
    MATMASTER_AGENT_NAME
)

from agents.matmaster_agent.organic_reaction_agent.prompt import (
    AgentDescription,
    AgentInstruction,
    ResultAgentDescription,
    ResultAgentName,
    ResultCoreAgentInstruction,
    ResultCoreAgentName,
    ResultTransferAgentInstruction,
    ResultTransferAgentName,
    SubmitAgentDescription,
    SubmitAgentName,
    SubmitCoreAgentDescription,
    SubmitCoreAgentInstruction,
    SubmitCoreAgentName,
    SubmitRenderAgentName,
    TransferAgentInstruction,
    TransferAgentName,
)

from agents.matmaster_agent.logger import matmodeler_logging_handler


autoTS = CalculationMCPToolset(
    connection_params=SseServerParams(url=ORGANIC_REACTION_SERVER_URL),
    executor=ORGANIC_REACTION_BOHRIUM_EXECUTOR,
    storage=ORGANIC_REACTION_BOHRIUM_STORAGE,
    async_mode=True,
    wait=False,
    logging_callback=matmodeler_logging_handler,
)

tools = [autoTS]


class OragnicReactionAgent(BaseAsyncJobAgent):
    def __init__(self, llm_config):
        super().__init__(
            agent_name=ORGANIC_REACTION_AGENT_NAME,
            model=llm_config.gpt_4o,
            agent_description=description,
            agent_instruction=instruction_en,
            mcp_tools=tools,
            submit_core_agent_class=SubmitCoreCalculationMCPLlmAgent,
            submit_core_agent_name=SubmitCoreAgentName,
            submit_core_agent_description=SubmitCoreAgentDescription,
            submit_core_agent_instruction=SubmitCoreAgentInstruction,
            submit_render_agent_name=SubmitRenderAgentName,
            result_core_agent_class=ResultCalculationMCPLlmAgent,
            result_core_agent_name=ResultCoreAgentName,
            result_core_agent_instruction=ResultCoreAgentInstruction,
            result_transfer_agent_name=ResultTransferAgentName,
            result_transfer_agent_instruction=ResultTransferAgentInstruction,
            transfer_agent_name=TransferAgentName,
            transfer_agent_instruction=TransferAgentInstruction,
            submit_agent_name=SubmitAgentName,
            submit_agent_description=SubmitAgentDescription,
            result_agent_name=ResultAgentName,
            result_agent_description=ResultAgentDescription,
            dflow_flag=False,
            supervisor_agent=MATMASTER_AGENT_NAME
        )

def init_organic_reaction_agent(llm_config) -> LlmAgent:
    return OragnicReactionAgent(llm_config)