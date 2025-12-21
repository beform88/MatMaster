from typing import Any

from pydantic import model_validator

from agents.matmaster_agent.base_agents.abc_agent import BaseMixin
from agents.matmaster_agent.base_agents.climit_agent import (
    content_limit_callback_mixin,
)
from agents.matmaster_agent.base_agents.error_agent import (
    ErrorHandleLlmAgent,
)


def disallow_transfer_model_validator(data: Any):
    if not isinstance(data, dict):
        return data

    data['disallow_transfer_to_parent'] = True
    data['disallow_transfer_to_peers'] = True

    return data


class CombinedDisallowTransferAndContentLimitMixin(BaseMixin):
    @model_validator(mode='before')
    @classmethod
    def decorate_callbacks(cls, data: Any) -> Any:
        return disallow_transfer_model_validator(content_limit_callback_mixin(data))


class DisallowTransferAndContentLimitLlmAgent(
    CombinedDisallowTransferAndContentLimitMixin, ErrorHandleLlmAgent
):
    pass
