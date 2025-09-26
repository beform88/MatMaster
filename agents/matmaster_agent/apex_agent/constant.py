import copy

from agents.matmaster_agent.constant import CURRENT_ENV, BohriumExecutor, BohriumStorge

# Agent Name
ApexAgentName = 'apex_agent'

# MCP Server URL
if CURRENT_ENV in ['test', 'uat']:
    ApexServerUrl = 'http://ysjl1373062.bohrium.tech:50001/sse'
else:
    # ApexServerUrl = "http://ysjl1373062.bohrium.tech:50001/sse"
    ApexServerUrl = 'https://apex-prime-uuid1754990126.app-space.dplink.cc/sse?token=7ab16179304d4a9b84cb270ff97b2979'
# APEX专用的Bohrium执行器配置
ApexBohriumExecutor = copy.deepcopy(BohriumExecutor)
ApexBohriumExecutor['machine']['remote_profile']['machine_type'] = 'c2_m8_cpu'

if CURRENT_ENV in ['test', 'uat']:
    # test
    ApexBohriumExecutor['machine']['remote_profile'][
        'image_address'
    ] = 'registry.dp.tech/dptech/dp/native/prod-16664/apex-agent-test-acs:0.0.4'
else:
    # prod
    ApexBohriumExecutor['machine']['remote_profile'][
        'image_address'
    ] = 'registry.dp.tech/dptech/dp/native/prod-16664/apex-agent-prod:0.1.2'


# APEX专用的Bohrium存储配置
ApexBohriumStorage = copy.deepcopy(BohriumStorge)
