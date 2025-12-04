from dotenv import load_dotenv
from dp.agent.adapter.adk import CalculationMCPToolset
from google.adk.agents import BaseAgent
from google.adk.tools.mcp_tool.mcp_session_manager import SseServerParams

from agents.matmaster_agent.base_agents.public_agent import (
    BaseSyncAgentWithToolValidator,
)
from agents.matmaster_agent.constant import (
    LOCAL_EXECUTOR,
    MATMASTER_AGENT_NAME,
    BohriumStorge,
)
from agents.matmaster_agent.llm_config import LLMConfig
from agents.matmaster_agent.sub_agents.STEEL_PREDICT_agent.constant import (
    STEEL_PREDICT_SERVER_URL,
)
from agents.matmaster_agent.sub_agents.STEEL_PREDICT_agent.prompt import (
    STEELPredictAgentDescription,
    STEELPredictAgentInstruction,
    STEELPredictAgentName,
)

load_dotenv()

# Initialize MCP tools for STEEL_PREDICT
steel_predict_toolset = CalculationMCPToolset(
    connection_params=SseServerParams(url=STEEL_PREDICT_SERVER_URL),
    storage=BohriumStorge,
    executor=LOCAL_EXECUTOR,
)


class STEELPredictAgent(BaseSyncAgentWithToolValidator):
    def __init__(self, llm_config: LLMConfig, name_suffix=''):
        super().__init__(
            model=llm_config.default_litellm_model,
            doc_summary=False,
            name=STEELPredictAgentName + name_suffix,
            description=STEELPredictAgentDescription,
            instruction=STEELPredictAgentInstruction,
            tools=[steel_predict_toolset],
            render_tool_response=False,
            supervisor_agent=MATMASTER_AGENT_NAME,
        )


def init_steel_predict_agent(llm_config: LLMConfig, name_suffix='') -> BaseAgent:
    return STEELPredictAgent(llm_config, name_suffix)
