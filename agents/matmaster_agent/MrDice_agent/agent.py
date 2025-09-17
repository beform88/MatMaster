from google.adk.agents import BaseAgent

from agents.matmaster_agent.MrDice_agent.openlam_agent.agent import init_openlam_database_agent
from agents.matmaster_agent.MrDice_agent.optimade_agent.agent import init_optimade_database_agent
from agents.matmaster_agent.MrDice_agent.bohriumpublic_agent.agent import init_bohriumpublic_database_agent
from agents.matmaster_agent.MrDice_agent.prompt import *
from agents.matmaster_agent.base_agents.llm_wrap_agent import LlmWrapAgent
from agents.matmaster_agent.constant import MATMASTER_AGENT_NAME


class MrDice_Agent(LlmWrapAgent):
    def __init__(self, llm_config):
        optimade_agent = init_optimade_database_agent(llm_config)
        openlam_agent = init_openlam_database_agent(llm_config)
        bohriumpublic_agent = init_bohriumpublic_database_agent(llm_config)
        super().__init__(
            model=llm_config.gpt_5_chat,
            name=MrDiceAgentName,
            description=MrDiceAgentDescription,
            instruction=MrDiceAgentInstruction,
            sub_agents=[
                optimade_agent,
                openlam_agent,
                bohriumpublic_agent,
            ],
            supervisor_agent=MATMASTER_AGENT_NAME
        )


def init_MrDice_agent(llm_config) -> BaseAgent:
    return MrDice_Agent(llm_config)
