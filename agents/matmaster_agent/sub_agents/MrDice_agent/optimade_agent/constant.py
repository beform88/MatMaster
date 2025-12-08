from agents.matmaster_agent.constant import CURRENT_ENV

OPTIMADE_DATABASE_AGENT_NAME = 'optimade_agent'

if CURRENT_ENV in ['test', 'uat']:
    OPTIMADE_URL = 'http://cmaz1395916.bohrium.tech:50004/sse'
else:
    OPTIMADE_URL = 'http://bowd1412840.bohrium.tech:50004/sse'
