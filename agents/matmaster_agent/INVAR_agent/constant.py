import copy

from agents.matmaster_agent.constant import BohriumExecutor, BohriumStorge, CURRENT_ENV

INVAR_AGENT_NAME = "invar_agent"
# if CURRENT_ENV in ["test", "uat"]:
#     INVARMCPServerUrl = "http://pfmx1355864.bohrium.tech:50004/sse"
# else:
#     INVARMCPServerUrl = "https://dart-uuid1754393230.app-space.dplink.cc/sse?token=ef35b35bd266483ebc6f0db75751ab54"

INVARMCPServerUrl = "http://pfmx1355864.bohrium.tech:50004/sse"
INVAR_BOHRIUM_EXECUTOR = copy.deepcopy(BohriumExecutor)
INVAR_BOHRIUM_EXECUTOR["machine"]["remote_profile"]["image_address"] = \
    "registry.dp.tech/dptech/dpa-calculator:81a7d87e"
INVAR_BOHRIUM_STORAGE = copy.deepcopy(BohriumStorge)