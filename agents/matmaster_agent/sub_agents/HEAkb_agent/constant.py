from agents.matmaster_agent.constant import CURRENT_ENV

HEA_KB_AGENT_NAME = 'HEAkb_agent'

if CURRENT_ENV in ['test', 'uat', 'prod']:
    HEA_SERVER_URL = 'http://lmnm1410647.bohrium.tech:50001/sse'
else:
    HEA_SERVER_URL = 'http://lmnm1410647.bohrium.tech:50001/sse'  # Default to prod if env not recognized
