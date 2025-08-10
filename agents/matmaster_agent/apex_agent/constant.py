import copy

from agents.matmaster_agent.constant import BohriumExecutor, BohriumStorge

# Agent Name
ApexAgentName = "apex_agent"

# MCP Server URL
ApexServerUrl = "http://hoxz1368496.bohrium.tech:50001/sse"
#ApexServerUrl = "http://0.0.0.0:50001/sse"

# APEX专用的Bohrium执行器配置
ApexBohriumExecutor = copy.deepcopy(BohriumExecutor)
ApexBohriumExecutor["machine"]["remote_profile"]["image_address"] = \
    "registry.dp.tech/dptech/dp/native/prod-16664/apex-agent:0.1.3"


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

# MCP工具名称 (v4更新：apex_process_calculation_results已集成到apex_calculate_properties中)
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

# Bohrium相关常量
BOHRIUM_JOB_LINKS = {
    "jobs_portal": "https://bohrium.dp.tech/jobs",
    "detail_template": "https://bohrium.dp.tech/jobs/detail/{job_id}"
}

# Bohrium认证配置方式更新
BOHRIUM_AUTH_METHOD = {
    "type": "config_file_embedded",
    "description": "认证信息嵌入在APEX配置文件中",
    "fields": ["bohrium_username", "bohrium_ticket", "bohrium_project_id"]
}