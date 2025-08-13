import os
from agents.matmaster_agent.constant import CURRENT_ENV

# Agent Name
PerovskiteAgentName = "perovskite_plot_agent"


# MCP Server URL for Perovskite Plot server

if CURRENT_ENV in ["test", "uat"]:
    PEROVSKITE_PLOT_URL = "http://cbqz1338812.bohrium.tech:50003/sse"
else:
    PEROVSKITE_PLOT_URL = "http://cbqz1338812.bohrium.tech:50004/sse"
