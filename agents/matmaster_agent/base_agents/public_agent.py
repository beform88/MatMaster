import logging

from google.adk.agents import SequentialAgent
from pydantic import computed_field, model_validator

from agents.matmaster_agent.base_agents.disallow_mcp_agent import (
    DisallowTransferSyncMCPAgent,
)
from agents.matmaster_agent.base_agents.recommend_summary_agent.agent import (
    BaseAgentWithRecAndSum,
)
from agents.matmaster_agent.base_agents.subordinate_agent import (
    SubordinateFeaturesMixin,
)
from agents.matmaster_agent.base_agents.sync_agent import (
    SyncMCPAgent,
)
from agents.matmaster_agent.base_agents.validator_agent import ValidatorAgent
from agents.matmaster_agent.constant import MATMASTER_AGENT_NAME
from agents.matmaster_agent.logger import PrefixFilter

logger = logging.getLogger(__name__)
logger.addFilter(PrefixFilter(MATMASTER_AGENT_NAME))
logger.setLevel(logging.INFO)


# 同步计算 Agent，可自动 transfer 回主 Agent
class BaseSyncAgent(SubordinateFeaturesMixin, SyncMCPAgent):
    pass


class BaseSyncAgentWithToolValidator(BaseAgentWithRecAndSum):
    @model_validator(mode='after')
    def after_init(self):
        self = self._after_init()
        agent_prefix = self.name.replace('_agent', '')

        sync_mcp_agent = DisallowTransferSyncMCPAgent(
            model=self.model,
            name=f"{agent_prefix}_sync_mcp_agent",
            tools=self.tools,
            after_model_callback=self.after_model_callback,
            after_tool_callback=self.after_tool_callback,
            before_tool_callback=self.before_tool_callback,
            enable_tgz_unpack=self.enable_tgz_unpack,
            cost_func=self.cost_func,
            render_tool_response=self.render_tool_response,
        )

        tool_validator_agent = ValidatorAgent(
            name=f"{agent_prefix}_tool_validator_agent", validator_key='tools_count'
        )

        self._submit_agent = SequentialAgent(
            name=f"{agent_prefix}_submit_agent",
            sub_agents=[sync_mcp_agent, tool_validator_agent],
        )

        self.sub_agents = [
            self.tool_call_info_agent,
            self.recommend_params_agent,
            self.submit_agent,
        ]

        return self

    @computed_field
    @property
    def submit_agent(self) -> SequentialAgent:
        return self._submit_agent
