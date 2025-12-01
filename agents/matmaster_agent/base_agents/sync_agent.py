from agents.matmaster_agent.base_agents.mcp_agent import (
    MCPAgent,
    MCPRunEventsMixin,
)


class SyncMCPAgent(MCPRunEventsMixin, MCPAgent):
    pass
