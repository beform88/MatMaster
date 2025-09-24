from agents.matmaster_agent.constant import CURRENT_ENV

MOFDB_DATABASE_AGENT_NAME = 'mofdb_agent'

if CURRENT_ENV in ['test', 'uat']:
    MOFDB_URL="http://bekc1366122.bohrium.tech:50004/sse"
    # MOFDB_URL = 'http://jjxr1366132.bohrium.tech:50003/sse'
else:
    MOFDB_URL = 'https://mr-dice-mofdb-uuid1758704787.app-space.dplink.cc/sse?token=c15a46f6440d41b086aca38446d959bf'
