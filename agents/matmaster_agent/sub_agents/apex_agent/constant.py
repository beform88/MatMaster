import copy

from agents.matmaster_agent.constant import CURRENT_ENV, BohriumExecutor, BohriumStorge

# Agent Name
ApexAgentName = 'apex_agent'

# MCP Server URL
if CURRENT_ENV in ['test', 'uat']:
    ApexServerUrl = 'http://rtvq1394775.bohrium.tech:50001/mcp'
else:
    # ApexServerUrl = 'http://rtvq1394775.bohrium.tech:50001/mcp'
    ApexServerUrl = 'https://apex-prime-uuid1754990126.appspace.bohrium.com/mcp?token=334be07f71404e92bf7ab7eb4350f1ac'
# APEX专用的Bohrium执行器配置
ApexBohriumExecutor = copy.deepcopy(BohriumExecutor)

ApexBohriumExecutor['machine']['remote_profile'][
    'image_address'
] = 'registry.dp.tech/dptech/dp/native/prod-16664/apex-agent-all:0.2.7'

# APEX专用的Bohrium存储配置
ApexBohriumStorage = copy.deepcopy(BohriumStorge)
