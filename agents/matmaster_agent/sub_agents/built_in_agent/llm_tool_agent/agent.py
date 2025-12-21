import copy
from typing import AsyncGenerator

from google.adk.agents import InvocationContext
from google.adk.events import Event

from agents.matmaster_agent.core_agents.comp_agents.dntransfer_climit_agent import (
    DisallowTransferAndContentLimitLlmAgent,
)
from agents.matmaster_agent.core_agents.comp_agents.error_climit_agent import (
    ErrorHandleAndContentLimitLlmAgent,
)
from agents.matmaster_agent.flow_agents.model import PlanStepStatusEnum
from agents.matmaster_agent.llm_config import LLMConfig
from agents.matmaster_agent.sub_agents.built_in_agent.llm_tool_agent.constant import (
    TOOL_AGENT_NAME,
)
from agents.matmaster_agent.utils.event_utils import update_state_event


class LLMToolAgent(DisallowTransferAndContentLimitLlmAgent):
    def __init__(self, llm_config: LLMConfig):
        super().__init__(
            model=llm_config.default_litellm_model,
            name=TOOL_AGENT_NAME,
            description='',
            instruction='Do not end with any question or prompt for user action.',
        )

    async def _run_events(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        async for event in super()._run_events(ctx):
            yield event

        update_plan = copy.deepcopy(ctx.session.state['plan'])
        update_plan['steps'][ctx.session.state['plan_index']][
            'status'
        ] = PlanStepStatusEnum.SUCCESS
        yield update_state_event(ctx, state_delta={'plan': update_plan})


def init_tool_agent(llm_config) -> ErrorHandleAndContentLimitLlmAgent:
    return LLMToolAgent(llm_config)
