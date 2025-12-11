import copy

from agents.matmaster_agent.constant import (
    CURRENT_ENV,
    BohriumExecutor,
    BohriumStorge,
)

PROPOSMATER_AGENT_NAME = 'proposmaster_agent'

if CURRENT_ENV in ['test', 'uat']:
    PROPOSMATER_MCP_SERVER_URL = 'http://iptk1405452.bohrium.tech:50002/sse'
else:
    PROPOSMATER_MCP_SERVER_URL = 'http://iptk1405452.bohrium.tech:50004/sse'

PROPOSMATER_BOHRIUM_EXECUTOR = copy.deepcopy(BohriumExecutor)
PROPOSMATER_BOHRIUM_EXECUTOR['machine']['remote_profile'][
    'image_address'
] = 'registry.dp.tech/dptech/dp/native/prod-13211/python:3.10'
PROPOSMATER_BOHRIUM_EXECUTOR['machine']['remote_profile']['machine_type'] = 'c2_m4_cpu'
PROPOSMATER_BOHRIUM_STORAGE = copy.deepcopy(BohriumStorge)
