from agents.matmaster_agent.constant import CURRENT_ENV

STEEL_PREDICT_AGENT_NAME = 'STEEL_PREDICT_agent'

# STEEL_PREDICT Server URL (SSE endpoint)
# Default port is 50001, but can be configured via environment or server settings
if CURRENT_ENV in ['test', 'uat', 'prod']:
    STEEL_PREDICT_SERVER_URL = 'http://lmnm1410647.bohrium.tech:50005/sse'
else:
    STEEL_PREDICT_SERVER_URL = 'http://lmnm1410647.bohrium.tech:50005/sse'  # Default to prod if env not recognized

