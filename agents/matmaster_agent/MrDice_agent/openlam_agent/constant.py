OPENLAM_DATABASE_AGENT_NAME = 'openlam_agent'

from agents.matmaster_agent.constant import CURRENT_ENV

if CURRENT_ENV in ['test', 'uat']:
    # OPTIMADE_URL="http://bekc1366122.bohrium.tech:50001/sse"
    OPENLAM_URL='http://bekc1366122.bohrium.tech:50002/sse'
else:
    OPENLAM_URL = 'https://material-data-retriever-uuid1754467958.app-space.dplink.cc/sse?token=16a1dd29dbb54cf9bf75748ba8df282d'
