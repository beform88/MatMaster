from agents.matmaster_agent.constant import CURRENT_ENV

BOHRIUMPUBLIC_DATABASE_AGENT_NAME = 'bohriumpublic_agent'

if CURRENT_ENV in ['test', 'uat']:
    BOHRIUMPUBLIC_URL = 'http://cmaz1395916.bohrium.tech:50001/sse'
else:
    BOHRIUMPUBLIC_URL = 'http://bowd1412840.bohrium.tech:50001/sse'
