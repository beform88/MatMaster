from agents.matmaster_agent.constant import CURRENT_ENV


SCIENCE_NAVIGATOR_AGENT_NAME = 'science_navigator_agent'

# MCP Server URLs for different environments
if CURRENT_ENV == 'test':
    SCIENCE_NAVIGATOR_MCP_SERVER_URL = "http://bohrium-mcp-internal.test.dp.tech:11003/sse"
elif CURRENT_ENV == 'uat':
    SCIENCE_NAVIGATOR_MCP_SERVER_URL = "http://bohrium-mcp-internal.uat.dp.tech:11003/sse"
else:
    SCIENCE_NAVIGATOR_MCP_SERVER_URL = "http://bohrium-mcp-internal.dp.tech:11003/sse"
