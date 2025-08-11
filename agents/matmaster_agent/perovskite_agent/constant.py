import os


# Agent Name
PerovskiteAgentName = "perovskite_plot_agent"


# MCP Server URL for Perovskite Plot server
# Can be overridden via environment variable `PEROVSKITE_PLOT_URL`
PEROVSKITE_PLOT_URL = os.getenv(
    "PEROVSKITE_PLOT_URL",
    "https://perovskite-plot-uuid1753420531.app-space.dplink.cc/sse?token=c26f7b921bfb440f8dafb7393388a412",
)


