from google.adk.agents import BaseAgent

from agents.matmaster_agent.base_agents.llm_wrap_agent import LlmWrapAgent
from agents.matmaster_agent.constant import MATMASTER_CORE_AGENT_NAME
from agents.matmaster_agent.MrDice_agent.bohriumpublic_agent.agent import (
    init_bohriumpublic_database_agent,
)
from agents.matmaster_agent.MrDice_agent.mofdb_agent.agent import (
    init_mofdb_database_agent,
)
from agents.matmaster_agent.MrDice_agent.openlam_agent.agent import (
    init_openlam_database_agent,
)
from agents.matmaster_agent.MrDice_agent.optimade_agent.agent import (
    init_optimade_database_agent,
)
from agents.matmaster_agent.MrDice_agent.prompt import (
    MrDiceAgentDescription,
    MrDiceAgentInstruction,
    MrDiceAgentName,
)


class MrDice_Agent(LlmWrapAgent):
    def __init__(self, llm_config):
        optimade_agent = init_optimade_database_agent(llm_config)
        openlam_agent = init_openlam_database_agent(llm_config)
        bohriumpublic_agent = init_bohriumpublic_database_agent(llm_config)
        mofdb_agent = init_mofdb_database_agent(llm_config)
        super().__init__(
            model=llm_config.gpt_5_chat,
            name=MrDiceAgentName,
            description=MrDiceAgentDescription,
            instruction=MrDiceAgentInstruction,
            sub_agents=[
                optimade_agent,
                openlam_agent,
                bohriumpublic_agent,
                mofdb_agent,
            ],
            supervisor_agent=MATMASTER_CORE_AGENT_NAME,
        )


def init_MrDice_agent(llm_config) -> BaseAgent:
    return MrDice_Agent(llm_config)
