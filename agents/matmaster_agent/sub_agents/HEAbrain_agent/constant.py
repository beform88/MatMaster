from agents.matmaster_agent.constant import CURRENT_ENV

HEA_BRAIN_AGENT_NAME = 'HEAbrain_agent'

if CURRENT_ENV in ['test', 'uat']:
    HEA_SERVER_URL = 'http://keld1409173.bohrium.tech:50005/sse'
    # TODO: Add test/uat specific URL if needed
else:
    HEA_SERVER_URL = 'http://keld1409173.bohrium.tech:50005/sse'
