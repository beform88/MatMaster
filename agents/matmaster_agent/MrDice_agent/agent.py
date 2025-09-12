from dotenv import load_dotenv
from dp.agent.adapter.adk import CalculationMCPToolset
from google.adk.agents import BaseAgent
from google.adk.tools.mcp_tool.mcp_session_manager import SseServerParams

from agents.matmaster_agent.base_agents.job_agent import CalculationMCPLlmAgent
from agents.matmaster_agent.constant import (
    LOCAL_EXECUTOR,
    BohriumStorge, MATMASTER_AGENT_NAME,
)
from agents.matmaster_agent.MrDice_agent.optimade_agent.agent import init_optimade_database_agent
from agents.matmaster_agent.MrDice_agent.openlam_agent.agent import init_openlam_database_agent
from agents.matmaster_agent.MrDice_agent.prompt import *
from agents.matmaster_agent.MrDice_agent.constant import *

load_dotenv()


class MrDice_Agent(CalculationMCPLlmAgent):
    def __init__(self, llm_config):
        optimade_agent = init_optimade_database_agent(llm_config)
        openlam_agent = init_openlam_database_agent(llm_config)
        super().__init__(
            model=llm_config.gpt_5_chat,
            name=MrDiceAgentName,
            description=MrDiceAgentDescription,
            instruction=MrDiceAgentInstruction,
            sub_agents=[
                optimade_agent,
                openlam_agent,
            ],
            render_tool_response=True,
            supervisor_agent=MATMASTER_AGENT_NAME
        )



def init_MrDice_agent(llm_config) -> BaseAgent:
    return MrDice_Agent(llm_config)
