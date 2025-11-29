from typing import Any

from pydantic import model_validator

from agents.matmaster_agent.base_agents.abc_agent import BaseMixin
from agents.matmaster_agent.base_agents.disallow_transfer_agent import (
    disallow_transfer_model_validator,
)
from agents.matmaster_agent.base_agents.error_agent import ErrorHandleLlmAgent
from agents.matmaster_agent.base_agents.mcp_agent import (
    MCPAgent,
    MCPInitMixin,
    MCPRunEventsMixin,
    mcp_callback_model_validator,
)


class SyncMCPAgent(MCPRunEventsMixin, MCPAgent):
    pass


class CombinedDisallowTransferAndMCPCallbackMixin(BaseMixin):
    @model_validator(mode='before')
    @classmethod
    def decorate_callbacks(cls, data: Any) -> Any:
        return disallow_transfer_model_validator(mcp_callback_model_validator(data))


class DisallowTransferSyncMCPAgent(
    MCPInitMixin,
    CombinedDisallowTransferAndMCPCallbackMixin,
    MCPRunEventsMixin,
    ErrorHandleLlmAgent,
):
    pass
