from agents.matmaster_agent.constant import CURRENT_ENV

POLYMER_KB_AGENT_NAME = 'POLYMERkb_agent'

# POLYMERkb Structured Search Server URL (SSE endpoint)
if CURRENT_ENV in ['test', 'uat', 'prod']:
    POLYMER_SERVER_URL = 'http://lmnm1410647.bohrium.tech:50003/sse'
else:
    POLYMER_SERVER_URL = 'http://lmnm1410647.bohrium.tech:50003/sse'  # Default to prod if env not recognized
