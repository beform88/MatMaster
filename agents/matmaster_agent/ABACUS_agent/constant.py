import copy

from agents.matmaster_agent.constant import BohriumExecutor, BohriumStorge, LOCAL_EXECUTOR, CURRENT_ENV

if CURRENT_ENV in ['test', 'uat']:
    ABACUS_CALCULATOR_URL = 'http://tfhs1357255.bohrium.tech:50001/sse'
else:
    ABACUS_CALCULATOR_URL = 'https://abacus-agent-tools-uuid1751014104.app-space.dplink.cc/sse?token=7cae849e8a324f2892225e070443c45b'
ABACUS_AGENT_NAME = 'ABACUS_calculation_agent'
ABACUS_CALCULATOR_BOHRIUM_EXECUTOR = copy.deepcopy(BohriumExecutor)
ABACUS_CALCULATOR_BOHRIUM_EXECUTOR['machine']['remote_profile']['image_address'] = \
    'registry.dp.tech/dptech/dp/native/prod-22618/abacusagenttools:v0.2-pre-20250822'
ABACUS_CALCULATOR_BOHRIUM_STORAGE = copy.deepcopy(BohriumStorge)

EXECUTOR_MAP = {
    'abacus_prepare': LOCAL_EXECUTOR,
    'abacus_modify_input': LOCAL_EXECUTOR,
    'abacus_modify_stru': LOCAL_EXECUTOR,
    'abacus_collect_data': LOCAL_EXECUTOR,
}
