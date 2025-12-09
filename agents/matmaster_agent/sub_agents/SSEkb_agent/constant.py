from agents.matmaster_agent.constant import CURRENT_ENV

SSE_KB_AGENT_NAME = 'SSEkb_agent'

# SSEkb Structured Search Server URL (SSE endpoint)
if CURRENT_ENV in ['test', 'uat']:
    SSE_SERVER_URL = 'http://lmnm1410647.bohrium.tech:50002/sse'
else:
    SSE_SERVER_URL = 'http://fwne1412142.bohrium.tech:50002/sse'  # Default to prod if env not recognized
