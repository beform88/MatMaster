from agents.matmaster_agent.constant import CURRENT_ENV

SuperconductorAgentName = 'superconductor_agent'
if CURRENT_ENV in ['test', 'uat']:
    SuperconductorServerUrl = 'http://root@mllo1368252.bohrium.tech:50002/sse'
else:
    SuperconductorServerUrl = 'https://superconductor-ambient-010-uuid1750845273.appspace.bohrium.com/sse?token=508f784b29d748af898819c6534a2fc2'
