from agents.matmaster_agent.base_agents.climit_mcp_agent import ContentLimitMCPAgent
from agents.matmaster_agent.base_agents.mcp_agent import (
    MCPRunEventsMixin,
)
from agents.matmaster_agent.base_agents.subordinate_agent import (
    SubordinateFeaturesMixin,
)


class BaseSyncAgent(SubordinateFeaturesMixin, MCPRunEventsMixin, ContentLimitMCPAgent):
    pass
