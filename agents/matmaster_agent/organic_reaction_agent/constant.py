import copy

from agents.matmaster_agent.constant import BohriumExecutor, BohriumStorge

ORGANIC_REACTION_AGENT_NAME = "organic_reaction_agent"
ORGANIC_REACTION_SERVER_URL = "http://iynz1366856.bohrium.tech:50001/sse"

ORGANIC_REACTION_BOHRIUM_EXECUTOR = copy.deepcopy(BohriumExecutor)
ORGANIC_REACTION_BOHRIUM_EXECUTOR["machine"]["remote_profile"]["image_address"] = \
    "registry.dp.tech/dptech/dp/native/prod-13364/autots:0.0.2"
ORGANIC_REACTION_BOHRIUM_STORAGE = copy.deepcopy(BohriumStorge)
