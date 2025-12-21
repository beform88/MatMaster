from typing import Any

from pydantic import model_validator

from agents.matmaster_agent.base_agents.abc_agent import BaseMixin
from agents.matmaster_agent.base_agents.climit_agent import content_limit_callback_mixin
from agents.matmaster_agent.base_agents.error_agent import ErrorHandleLlmAgent
from agents.matmaster_agent.base_agents.mcp_agent import (
    MCPInitMixin,
    mcp_callback_model_validator,
)


class CombinedContentLimitAndMCPCallbackMixin(BaseMixin):
    @model_validator(mode='before')
    @classmethod
    def decorate_callbacks(cls, data: Any) -> Any:
        return content_limit_callback_mixin(mcp_callback_model_validator(data))


class ContentLimitMCPAgent(
    MCPInitMixin, CombinedContentLimitAndMCPCallbackMixin, ErrorHandleLlmAgent
):
    pass
