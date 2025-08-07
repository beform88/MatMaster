import copy

from agents.matmaster_agent.constant import BohriumExecutor, BohriumStorge

AUTODE_AGENT_NAME = "autode_agent"
AUTODE_SERVER_URL = "https://7716d0fc31636914783865d34f6cdfd5.app-space.dplink.cc/sse?token=165623f1582845b2810d42d8d1799a24"
AUTODE_BOHRIUM_EXECUTOR = copy.deepcopy(BohriumExecutor)
AUTODE_BOHRIUM_EXECUTOR["machine"]["remote_profile"]["image_address"] = \
    "registry.dp.tech/dptech/dp/native/prod-13364/autots:0.0.2"
AUTODE_BOHRIUM_STORAGE = copy.deepcopy(BohriumStorge)