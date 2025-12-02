import copy

from agents.matmaster_agent.constant import CURRENT_ENV, BohriumExecutor, BohriumStorge

DOE_AGENT_NAME = 'doe_agent'

if CURRENT_ENV in ['test']:
    DOE_SERVER_URL = 'http://gvjj1410767.bohrium.tech:50001/sse'
elif CURRENT_ENV in ['uat']:
    DOE_SERVER_URL = 'http://gvjj1410767.bohrium.tech:50002/sse'
else:
    DOE_SERVER_URL = 'http://gvjj1410767.bohrium.tech:50003/sse'

DOE_BOHRIUM_EXECUTOR = copy.deepcopy(BohriumExecutor)
DOE_BOHRIUM_EXECUTOR['machine']['remote_profile'][
    'image_address'
] = 'registry.dp.tech/dptech/dp/native/prod-13375/unielf:v1.19.0-maunal'
DOE_BOHRIUM_EXECUTOR['machine']['remote_profile']['machine_type'] = 'c2_m8_cpu'
DOE_BOHRIUM_STORAGE = copy.deepcopy(BohriumStorge)
