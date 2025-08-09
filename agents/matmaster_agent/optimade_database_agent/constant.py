OPTIMADE_DATABASE_AGENT_NAME = "Optimade_Agent"

from agents.matmaster_agent.constant import CURRENT_ENV

if CURRENT_ENV in ["test", "uat"]:
    OPTIMADE_URL="http://jjxr1366132.bohrium.tech:50001/sse"
else:
    OPTIMADE_URL = "https://material-data-retriever-uuid1754467958.app-space.dplink.cc/sse?token=da492c56028540f5ba995d33f76baf8e"
