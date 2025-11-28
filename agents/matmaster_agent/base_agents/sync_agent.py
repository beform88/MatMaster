from agents.matmaster_agent.base_agents.disallow_transfer_agent import (
    DisallowTransferMixin,
)
from agents.matmaster_agent.base_agents.mcp_agent import (
    MCPAgent,
    MCPRunEventsMixin,
)


class SyncMCPAgent(MCPRunEventsMixin, MCPAgent):
    pass


class DisallowTransferSyncMCPAgent(DisallowTransferMixin, SyncMCPAgent):
    pass
