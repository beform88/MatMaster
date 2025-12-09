from agents.matmaster_agent.constant import CURRENT_ENV

MOFDB_DATABASE_AGENT_NAME = 'mofdb_agent'

if CURRENT_ENV in ['test', 'uat']:
    MOFDB_URL = 'http://cmaz1395916.bohrium.tech:50002/sse'
else:
    MOFDB_URL = 'http://bowd1412840.bohrium.tech:50002/sse'
