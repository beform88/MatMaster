import copy

from agents.matmaster_agent.constant import BohriumExecutor, BohriumStorge

# Agent Name
ApexAgentName = "apex_agent"

# MCP Server URL
ApexServerUrl = "http://hoxz1368496.bohrium.tech:50001/sse"

# APEX专用的Bohrium执行器配置
ApexBohriumExecutor = copy.deepcopy(BohriumExecutor)
ApexBohriumExecutor["machine"]["remote_profile"]["image_address"] = \
    "registry.dp.tech/dptech/dp/native/prod-16664/apex-agent:0.0.3"


# APEX专用的Bohrium存储配置
ApexBohriumStorage = copy.deepcopy(BohriumStorge) 