from agents.matmaster_agent.constant import CURRENT_ENV

StructureGenerateAgentName = 'structure_generate_agent'

if CURRENT_ENV == 'test':
    StructureGenerateServerUrl = 'http://qpus1389933.bohrium.tech:50003/sse'
elif CURRENT_ENV == 'uat':
    StructureGenerateServerUrl = 'https://93b71ff0836bb95466a9de7aaa34de09.appspace.uat.bohrium.com/sse?token=c46b37df6b9e46ce88986afa120b7f34'
else:
    StructureGenerateServerUrl = 'http://pfmx1355864.bohrium.tech:50003/sse'
    # StructureGenerateServerUrl = 'https://cystalformer-uuid1754551471.app-space.dplink.cc/sse?token=1750cd294e6c4270946ae37107a725ff'
