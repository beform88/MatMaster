from agents.matmaster_agent.constant import CURRENT_ENV

StructureGenerateAgentName = 'structure_generate_agent'

if CURRENT_ENV == 'test':
    StructureGenerateServerUrl = 'http://qpus1389933.bohrium.tech:50003/mcp'
elif CURRENT_ENV == 'uat':
    StructureGenerateServerUrl = 'https://93b71ff0836bb95466a9de7aaa34de09.appspace.uat.bohrium.com/sse?token=c46b37df6b9e46ce88986afa120b7f34'  # TODO: update uat url to mcp
else:
    # StructureGenerateServerUrl = 'http://pfmx1355864.bohrium.tech:50003/sse' # TODO: update backup prod url to mcp
    StructureGenerateServerUrl = 'https://structure-generator-uuid1767674194.appspace.bohrium.com/mcp?token=a297dc122dc74368af3d2e725991d559'
