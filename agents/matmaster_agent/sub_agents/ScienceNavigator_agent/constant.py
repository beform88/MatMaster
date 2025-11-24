import os
from dotenv import load_dotenv

from agents.matmaster_agent.constant import CURRENT_ENV

# 加载环境变量
load_dotenv()

SCIENCE_NAVIGATOR_AGENT_NAME = 'science_navigator_agent'

# MCP Server URLs for different environments
if CURRENT_ENV in ['test', 'uat']:
    SCIENCE_NAVIGATOR_MCP_SERVER_URL = "http://bohrium-mcp-internal.test.dp.tech:11003/sse" if CURRENT_ENV == 'test' else "http://bohrium-mcp-internal.uat.dp.tech:11003/sse"
else:
    SCIENCE_NAVIGATOR_MCP_SERVER_URL = "http://bohrium-mcp-internal.dp.tech:11003/sse"

# Storage configuration - matching the example
SCIENCE_NAVIGATOR_BOHRIUM_STORAGE = {
    "type": "https",
    "plugin": {
        "type": "bohrium",
        "access_key": os.getenv("MATERIALS_ACCESS_KEY", ""),
        "project_id": int(os.getenv("MATERIALS_PROJECT_ID", 0))
    }
}

# Executor configuration - matching the example
SCIENCE_NAVIGATOR_BOHRIUM_EXECUTOR = {
    "type": "local"
}