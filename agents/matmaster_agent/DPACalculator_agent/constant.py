import copy

from agents.matmaster_agent.constant import BohriumExecutor, BohriumStorge, CURRENT_ENV

DPACalulator_AGENT_NAME = "dpa_calculator_agent"
if CURRENT_ENV in ["test", "uat"]:
    DPAMCPServerUrl = "http://pfmx1355864.bohrium.tech:50001/sse"
else:
    DPAMCPServerUrl = "https://2b1905b5d4641830901acf76c957cfb1.app-space.dplink.cc/sse?token=c8470446801844a0a4f0e9f85f7f5587"
DPACalulator_BOHRIUM_EXECUTOR = copy.deepcopy(BohriumExecutor)
DPACalulator_BOHRIUM_EXECUTOR["machine"]["remote_profile"]["image_address"] = \
    "registry.dp.tech/dptech/dpa-calculator:9fb11626"
DPACalulator_BOHRIUM_EXECUTOR["machine"]["remote_profile"]["machine_type"] = \
    "1 * NVIDIA V100_32g"
DPACalulator_BOHRIUM_STORAGE = copy.deepcopy(BohriumStorge)
