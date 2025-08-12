import copy

from agents.matmaster_agent.constant import BohriumExecutor, BohriumStorge, CURRENT_ENV

DPACalulator_AGENT_NAME = "dpa_calculator_agent"
if CURRENT_ENV in ["test", "uat"]:
    DPAMCPServerUrl = "http://pfmx1355864.bohrium.tech:50001/sse"
else:
    DPAMCPServerUrl = "https://dpa-uuid1750659890.app-space.dplink.cc/sse?token=7c2e8de61ec94f4e80ebcef1ac17c92e"
DPACalulator_BOHRIUM_EXECUTOR = copy.deepcopy(BohriumExecutor)
DPACalulator_BOHRIUM_EXECUTOR["machine"]["remote_profile"]["image_address"] = \
    "registry.dp.tech/dptech/dpa-calculator:9fb11626"
DPACalulator_BOHRIUM_EXECUTOR["machine"]["remote_profile"]["machine_type"] = \
    "1 * NVIDIA V100_32g"
DPACalulator_BOHRIUM_STORAGE = copy.deepcopy(BohriumStorge)
