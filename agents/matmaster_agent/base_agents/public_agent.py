import logging
from typing import AsyncGenerator, Union, override

from google.adk.agents import InvocationContext
from google.adk.events import Event
from google.adk.models import BaseLlm
from pydantic import computed_field, model_validator

from agents.matmaster_agent.base_agents.error_agent import (
    ErrorHandleLlmAgent,
)
from agents.matmaster_agent.base_agents.mcp_agent import MCPInitMixin
from agents.matmaster_agent.base_agents.subordinate_agent import (
    SubordinateFeaturesMixin,
)
from agents.matmaster_agent.base_agents.sync_agent import (
    SyncMCPAgent,
    ToolValidatorAgent,
)
from agents.matmaster_agent.constant import (
    MATMASTER_AGENT_NAME,
)
from agents.matmaster_agent.logger import PrefixFilter
from agents.matmaster_agent.utils.event_utils import (
    update_state_event,
)

logger = logging.getLogger(__name__)
logger.addFilter(PrefixFilter(MATMASTER_AGENT_NAME))
logger.setLevel(logging.INFO)


# 同步计算 Agent，可自动 transfer 回主 Agent
class BaseSyncAgent(SubordinateFeaturesMixin, SyncMCPAgent):
    pass


class BaseSyncAgentWithToolValidator(
    SubordinateFeaturesMixin, MCPInitMixin, ErrorHandleLlmAgent
):
    model: Union[str, BaseLlm]
    instruction: str
    tools: list

    @model_validator(mode='after')
    def after_init(self):
        agent_prefix = self.name.replace('_agent', '')

        self._sync_mcp_agent = SyncMCPAgent(
            model=self.model,
            name=f"{agent_prefix}_sync_mcp_agent",
            description=self.description,
            instruction=self.instruction,
            tools=self.tools,
            disallow_transfer_to_peers=True,
            disallow_transfer_to_parent=True,
            after_model_callback=self.after_model_callback,
            enable_tgz_unpack=self.enable_tgz_unpack,
            cost_func=self.cost_func,
            render_tool_response=self.render_tool_response,
        )

        self._tool_validator_agent = ToolValidatorAgent(
            name=f"{agent_prefix}_tool_validator_agent",
        )

        self.sub_agents = [self.sync_mcp_agent, self.tool_validator_agent]

        return self

    @computed_field
    @property
    def sync_mcp_agent(self) -> SyncMCPAgent:
        return self._sync_mcp_agent

    @computed_field
    @property
    def tool_validator_agent(self) -> ToolValidatorAgent:
        return self._tool_validator_agent

    @override
    async def _run_events(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        yield update_state_event(ctx, state_delta={'tool_hallucination': False})
        for _ in range(2):
            async for sync_mcp_event in self.sync_mcp_agent.run_async(ctx):
                yield sync_mcp_event

            async for tool_validator_event in self.tool_validator_agent.run_async(ctx):
                yield tool_validator_event

            if not ctx.session.state['tool_hallucination']:
                break
