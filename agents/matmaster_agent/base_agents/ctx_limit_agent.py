from typing import Any

from google.adk.agents import LlmAgent
from pydantic import model_validator

from agents.matmaster_agent.base_agents.abc_agent import BaseMixin
from agents.matmaster_agent.base_callbacks.private_callback import (
    default_before_model_callback,
    filter_safety_content,
)


def content_limit_callback_mixin(data: Any):
    if not isinstance(data, dict):
        return data

    if data.get('before_model_callback') is None:
        data['before_model_callback'] = default_before_model_callback

    data['before_model_callback'] = filter_safety_content(data['before_model_callback'])

    return data


class ContentLimitMixin(BaseMixin):
    @model_validator(mode='before')
    @classmethod
    def decorate_callbacks(cls, data: Any) -> Any:
        return content_limit_callback_mixin(data)


class ContentLimitLlmAgent(ContentLimitMixin, LlmAgent):
    pass
