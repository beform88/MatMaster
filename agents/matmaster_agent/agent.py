from google.adk.agents import LlmAgent
from opik.integrations.adk import track_adk_agent_recursive

from agents.matmaster_agent.callback import matmaster_before_agent
from agents.matmaster_agent.constant import MATMASTER_AGENT_NAME
from agents.matmaster_agent.llm_config import MatMasterLlmConfig

from agents.matmaster_agent.autode_agent.agent import (
    init_autode_agent,
)

class MatMasterAgent(LlmAgent):
    def __init__(self, llm_config):
        super().__init__(
            name=MATMASTER_AGENT_NAME,
            model=llm_config.gpt_4o,
            sub_agents=[piloteye_electro_agent, dpa_calculator_agent, optimade_agent],
            before_agent_callback=matmaster_before_agent
        )


def init_matmaster_agent() -> LlmAgent:
    matmodeler_agent = MatMasterAgent(MatMasterLlmConfig)
    track_adk_agent_recursive(matmodeler_agent, MatMasterLlmConfig.opik_tracer)

    return matmodeler_agent


# Global instance of the agent
root_agent = init_matmaster_agent()
