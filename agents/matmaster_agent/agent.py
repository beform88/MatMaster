from google.adk.agents import LlmAgent
from opik.integrations.adk import track_adk_agent_recursive

from agents.matmaster_agent.llm_config import MatMasterLlmConfig


class MatMasterAgent(LlmAgent):
    def __init__(self, llm_config):
        super().__init__(
            model=llm_config.gpt_4o,
            name="matmaster_agent"
        )


def init_matmaster_agent() -> LlmAgent:
    matmodeler_agent = MatMasterAgent(MatMasterLlmConfig)
    track_adk_agent_recursive(matmodeler_agent, MatMasterLlmConfig.opik_tracer)

    return matmodeler_agent


# Global instance of the agent
root_agent = init_matmaster_agent()
