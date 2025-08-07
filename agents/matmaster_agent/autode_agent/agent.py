import os
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import SseServerParams, MCPToolset

from opik.integrations.adk import track_adk_agent_recursive

from agents.matmaster_agent.llm_config import MatMasterLlmConfig

from dp.agent.adapter.adk import CalculationMCPToolset

from agents.matmaster_agent.autode_agent.constant import (
    AUTODE_BOHRIUM_EXECUTOR,
    AUTODE_BOHRIUM_STORAGE,
    AUTODE_SERVER_URL,
    AUTODE_AGENT_NAME,
)
from agents.matmaster_agent.autode_agent.prompt import (
    description,
    instruction_en,
)


autoTS = CalculationMCPToolset(
    connection_params=SseServerParams(url=AUTODE_SERVER_URL),
    executor=AUTODE_BOHRIUM_EXECUTOR,
    storage=AUTODE_BOHRIUM_STORAGE,
)

tools = [autoTS]

class AutodEAgent(LlmAgent):
    def __init__(self, llm_config):
        super().__init__(
            name=AUTODE_AGENT_NAME,
            model=llm_config.gpt_4o,
            description=description,
            instruction=instruction_en,
            tools=tools,
        )

def init_autode_agent() -> LlmAgent:
    autode_agent = AutodEAgent(MatMasterLlmConfig)
    track_adk_agent_recursive(autode_agent, MatMasterLlmConfig.opik_tracer)

    return autode_agent

# root_agent = init_autode_agent()