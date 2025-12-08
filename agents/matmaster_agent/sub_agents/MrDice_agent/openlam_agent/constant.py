from agents.matmaster_agent.constant import CURRENT_ENV

OPENLAM_DATABASE_AGENT_NAME = 'openlam_agent'

if CURRENT_ENV in ['test', 'uat']:
    OPENLAM_URL = 'http://cmaz1395916.bohrium.tech:50003/sse'
else:
    OPENLAM_URL = 'http://bowd1412840.bohrium.tech:50003/sse'
