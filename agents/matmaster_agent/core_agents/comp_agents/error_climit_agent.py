from google.adk.agents import LlmAgent

from agents.matmaster_agent.core_agents.base_agents.climit_agent import (
    ContentLimitMixin,
)
from agents.matmaster_agent.core_agents.base_agents.error_agent import ErrorHandlerMixin


class ErrorHandleAndContentLimitLlmAgent(
    ErrorHandlerMixin, ContentLimitMixin, LlmAgent
):
    pass
