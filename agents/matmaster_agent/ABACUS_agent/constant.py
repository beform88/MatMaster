import copy

from agents.matmaster_agent.constant import BohriumExecutor, BohriumStorge, LOCAL_EXECUTOR

ABACUS_CALCULATOR_AGENT_NAME = "ABACUS_calculator_agent"
ABACUS_CALCULATOR_URL = 'http://tfhs1357255.bohrium.tech:50001/sse'
ABACUS_CALCULATOR_BOHRIUM_EXECUTOR = copy.deepcopy(BohriumExecutor)
ABACUS_CALCULATOR_BOHRIUM_EXECUTOR["machine"]["remote_profile"]["image_address"] = \
    "registry.dp.tech/dptech/dp/native/prod-22618/abacusagenttools:v0.1-20250807"
ABACUS_CALCULATOR_BOHRIUM_STORAGE = copy.deepcopy(BohriumStorge)

EXECUTOR_MAP = {
    "generate_bulk_structure": None,
    "generate_molecule_structure": None,
    "abacus_prepare": None,
    "abacus_modify_input": None,
    "abacus_modify_stru": None,
    "abacus_collect_data": None,
    "abacus_prepare_inputs_from_relax_results": None,
    "generate_bulk_structure_from_wyckoff_position": None,
}
