from google.adk.agents import BaseAgent
from opik.integrations.adk import track_adk_agent_recursive

from agents.matmaster_agent.llm_config import MatMasterLlmConfig


class MatMasterAgent(BaseAgent):
    def __init__(self, llm_config):
        super().__init__(
            model=llm_config.gpt_4o
        )


def init_matmaster_agent() -> BaseAgent:
    matmodeler_agent = MatMasterAgent(MatMasterLlmConfig)
    track_adk_agent_recursive(matmodeler_agent, MatMasterLlmConfig.opik_tracer)

    return matmodeler_agent


# Global instance of the agent
root_agent = init_matmaster_agent()
