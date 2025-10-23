from google.adk.agents import BaseAgent

from agents.matmaster_agent.base_agents.llm_wrap_agent import LlmWrapAgent
from agents.matmaster_agent.task_orchestrator_agent.constant import (
    TASK_ORCHESTRATOR_AGENT_NAME,
    TASK_ORCHESTRATOR_AGENT_DESCRIPTION,
)
from agents.matmaster_agent.task_orchestrator_agent.prompt import (
    TASK_ORCHESTRATOR_AGENT_INSTRUCTION,
    TASK_ORCHESTRATOR_AGENT_DESCRIPTION,
)
from agents.matmaster_agent.constant import MATMASTER_AGENT_NAME


class TaskOrchestratorAgent(LlmWrapAgent):
    """An agent that orchestrates complex workflows from brief user prompts."""
    
    def __init__(self, llm_config):
        super().__init__(
            model=llm_config.gpt_5_chat,
            name=TASK_ORCHESTRATOR_AGENT_NAME,
            description=TASK_ORCHESTRATOR_AGENT_DESCRIPTION,
            instruction=TASK_ORCHESTRATOR_AGENT_INSTRUCTION,
            supervisor_agent=MATMASTER_AGENT_NAME,
        )


def init_task_orchestrator_agent(llm_config) -> BaseAgent:
    """Initialize the task orchestrator agent."""
    return TaskOrchestratorAgent(llm_config)