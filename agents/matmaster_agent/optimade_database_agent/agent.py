from dotenv import load_dotenv
from dp.agent.adapter.adk import CalculationMCPToolset
from google.adk.agents import BaseAgent
from google.adk.tools.mcp_tool.mcp_session_manager import SseServerParams

from agents.matmaster_agent.base_agents.job_agent import CalculationMCPLlmAgent
from agents.matmaster_agent.constant import (
    LOCAL_EXECUTOR,
    BohriumStorge, MATMASTER_AGENT_NAME,
)
from agents.matmaster_agent.optimade_database_agent.constant import *
from agents.matmaster_agent.optimade_database_agent.prompt import *

load_dotenv()

# Initialize MCP tools and agent
mcp_tools = CalculationMCPToolset(
    connection_params=SseServerParams(url=OPTIMADE_URL),
    storage=BohriumStorge,
    executor=LOCAL_EXECUTOR
)


class Optimade_Agent(CalculationMCPLlmAgent):
    def __init__(self, llm_config):
        super().__init__(
            # model=llm_config.deepseek_chat,
            model=llm_config.gpt_4o,
            name=OptimadeAgentName,
            description=OptimadeAgentDescription,
            instruction=OptimadeAgentInstruction,
            tools=[mcp_tools],
            render_tool_response=True,
            supervisor_agent=MATMASTER_AGENT_NAME
        )


def init_optimade_database_agent(llm_config) -> BaseAgent:
    return Optimade_Agent(llm_config)
