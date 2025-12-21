from typing import Any

from pydantic import model_validator

from agents.matmaster_agent.core_agents.base_agents.abc_agent import BaseMixin
from agents.matmaster_agent.core_agents.base_agents.climit_agent import (
    content_limit_callback_mixin,
)
from agents.matmaster_agent.core_agents.base_agents.error_agent import (
    ErrorHandleLlmAgent,
)
from agents.matmaster_agent.core_agents.base_agents.mcp_agent import (
    MCPInitMixin,
    MCPRunEventsMixin,
    mcp_callback_model_validator,
)
from agents.matmaster_agent.core_agents.comp_agents.dntransfer_climit_agent import (
    disallow_transfer_model_validator,
)


class CombinedDisallowTransferAndContentLimitAndMCPCallbackMixin(BaseMixin):
    @model_validator(mode='before')
    @classmethod
    def decorate_callbacks(cls, data: Any) -> Any:
        return disallow_transfer_model_validator(
            content_limit_callback_mixin(mcp_callback_model_validator(data))
        )


class DisallowTransferAndContentLimitMCPAgent(
    MCPInitMixin,
    CombinedDisallowTransferAndContentLimitAndMCPCallbackMixin,
    ErrorHandleLlmAgent,
):
    pass


class DisallowTransferAndContentLimitSyncMCPAgent(
    MCPInitMixin,
    CombinedDisallowTransferAndContentLimitAndMCPCallbackMixin,
    MCPRunEventsMixin,
    ErrorHandleLlmAgent,
):
    pass
