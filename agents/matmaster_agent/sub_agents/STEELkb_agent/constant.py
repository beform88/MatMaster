from agents.matmaster_agent.constant import CURRENT_ENV

STEEL_KB_AGENT_NAME = 'STEELkb_agent'

# STEELkb RAG Server URL (SSE endpoint)
if CURRENT_ENV in ['test', 'uat']:
    STEEL_SERVER_URL = 'http://lmnm1410647.bohrium.tech:50004/sse'
else:
    STEEL_SERVER_URL = 'http://fwne1412142.bohrium.tech:50004/sse'  # Default to prod if env not recognized
