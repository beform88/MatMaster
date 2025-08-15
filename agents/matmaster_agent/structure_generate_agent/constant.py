from agents.matmaster_agent.constant import CURRENT_ENV

StructureGenerateAgentName = "structure_generate_agent"

if CURRENT_ENV in ["test", "uat"]:
    StructureGenerateServerUrl = "http://root@ouhw1371796.bohrium.tech:50001/sse"
else:
    StructureGenerateServerUrl = "https://983a33a9a86796df362c1108e00f54a6.app-space.dplink.cc/sse?token=f6b68584847b4a3ea52bf0e4f6290e97"