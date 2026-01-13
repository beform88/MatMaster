from agents.matmaster_agent.constant import CURRENT_ENV

StructureGenerateAgentName = 'structure_generate_agent'

if CURRENT_ENV == 'test':
    StructureGenerateServerUrl = 'http://qpus1389933.bohrium.tech:50003/mcp'
elif CURRENT_ENV == 'uat':
    StructureGenerateServerUrl = 'https://structure-generator-uat-2-uuid1767842266.appspace.uat.bohrium.com/mcp?token=45e714e2de6942829021f4c6e81971cf'
else:
    # StructureGenerateServerUrl = 'http://pfmx1355864.bohrium.tech:50003/sse' # TODO: update backup prod url to mcp
    StructureGenerateServerUrl = 'https://structure-generator-uuid1767674194.appspace.bohrium.com/mcp?token=a297dc122dc74368af3d2e725991d559'
