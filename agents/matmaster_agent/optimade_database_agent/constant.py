OPTIMADE_DATABASE_AGENT_NAME = "optimade_agent"

from agents.matmaster_agent.constant import CURRENT_ENV

if CURRENT_ENV in ["test", "uat"]:
    OPTIMADE_URL="http://jjxr1366132.bohrium.tech:50001/sse"
else:
    OPTIMADE_URL = "https://material-data-retriever-uuid1754467958.app-space.dplink.cc/sse?token=fe71bd9c5ffc4962aa2110e7ef25cc0f"