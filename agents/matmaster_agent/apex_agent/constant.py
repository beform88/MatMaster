import copy

from agents.matmaster_agent.constant import BohriumExecutor, BohriumStorge,CURRENT_ENV

# Agent Name
ApexAgentName = "apex_agent"

# MCP Server URL
if CURRENT_ENV in ["test", "uat"]:
    ApexServerUrl = "http://hoxz1368496.bohrium.tech:50001/sse"
else:
    ApexServerUrl = "https://3ce3bd7d63a2c9c81983cc8e9bd02ae5.app-space.dplink.cc/sse?token=33d662e586f34a9e8f26d9d4fce29f27"

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

# 结果处理相关常量
APEX_RESULT_PROCESSING_FEATURES = {
    "auto_markdown_generation": True,
    "chart_visualization": True,
    "structure_file_management": True,
    "result_file_download": True
}

# 支持的结果处理性质类型
APEX_SUPPORTED_RESULT_PROPERTIES = [
    "vacancy", "interstitial", "elastic", "surface", 
    "gamma", "phonon", "eos"
]

# MCP工具名称 
APEX_NEW_MCP_TOOLS = [
    "apex_list_user_files", 
    "apex_download_structure_file",
    "apex_cleanup_old_files"
]

# 任务状态相关常量
APEX_TASK_STATUSES = {
    "submitted": "已提交到Bohrium",
    "running": "正在运行",
    "completed": "已完成",
    "failed": "失败"
}


# Bohrium认证配置方式更新
BOHRIUM_AUTH_METHOD = {
    "type": "config_file_embedded",
    "description": "认证信息嵌入在APEX配置文件中",
    "fields": ["bohrium_username", "bohrium_ticket", "bohrium_project_id"]
}