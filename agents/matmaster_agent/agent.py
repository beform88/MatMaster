from google.adk.agents import LlmAgent
from opik.integrations.adk import track_adk_agent_recursive

from agents.matmaster_agent.base_agents.io_agent import HandleFileUploadLlmAgent
from agents.matmaster_agent.callback import matmaster_before_agent
from agents.matmaster_agent.constant import MATMASTER_AGENT_NAME
from agents.matmaster_agent.llm_config import MatMasterLlmConfig
from agents.matmaster_agent.piloteye_electro_agent.agent import init_piloteye_electro_agent
from agents.matmaster_agent.thermoelectric_agent.agent import init_thermoelectric_agent

from agents.matmaster_agent.prompt import GlobalInstruction, AgentInstruction, AgentDescription


class MatMasterAgent(HandleFileUploadLlmAgent):

    def __init__(self, llm_config):
        unielf_agent = init_piloteye_electro_agent(llm_config)
        thermoelectric_agent = init_thermoelectric_agent(llm_config)
        print(thermoelectric_agent.name)

        super().__init__(
            name=MATMASTER_AGENT_NAME,
            model=llm_config.gpt_4o,
            sub_agents=[unielf_agent, thermoelectric_agent],
            global_instruction=GlobalInstruction,
            instruction=AgentInstruction,
            description=AgentDescription,
            before_agent_callback=matmaster_before_agent
        )


def init_matmaster_agent() -> LlmAgent:
    matmodeler_agent = MatMasterAgent(MatMasterLlmConfig)
    track_adk_agent_recursive(matmodeler_agent, MatMasterLlmConfig.opik_tracer)

    return matmodeler_agent


# Global instance of the agent
root_agent = init_matmaster_agent()
