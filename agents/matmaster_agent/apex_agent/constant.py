import copy

from agents.matmaster_agent.constant import (
    BohriumExecutor,
    BohriumStorge,
    CURRENT_ENV,
)

# Agent Name
ApexAgentName = "apex_agent"

# MCP Server URL
if CURRENT_ENV in ["test", "uat"]:
    ApexServerUrl = "http://hoxz1368496.bohrium.tech:50001/sse"
else:
    #ApexServerUrl = "http://hoxz1368496.bohrium.tech:50001/sse"
    ApexServerUrl = "https://apex-prime-uuid1754990126.app-space.dplink.cc/sse?token=85c6ee4ceb12412e9c920a9d35388830"

# APEX专用的Bohrium执行器配置
ApexBohriumExecutor = copy.deepcopy(BohriumExecutor)

if CURRENT_ENV in ["test", "uat"]:
    # test
    ApexBohriumExecutor["machine"]["remote_profile"]["image_address"] = \
        "registry.dp.tech/dptech/dp/native/prod-16664/apex-agent-test:0.1.0"
else:
    # prod
    ApexBohriumExecutor["machine"]["remote_profile"]["image_address"] = \
        "registry.dp.tech/dptech/dp/native/prod-16664/apex-agent-prod:0.0.3"

# APEX专用的Bohrium存储配置
ApexBohriumStorage = copy.deepcopy(BohriumStorge)
