from agents.matmaster_agent.constant import CURRENT_ENV

StructureGenerateAgentName = "structure_generate_agent"

if CURRENT_ENV in ["test", "uat"]:
    StructureGenerateServerUrl = "http://root@ouhw1371796.bohrium.tech:50001/sse"
else:
    StructureGenerateServerUrl = "http://root@wkar1368227.bohrium.tech:50001/sse"