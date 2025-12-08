from agents.matmaster_agent.constant import CURRENT_ENV

ThermoelectricAgentName = 'thermoelectric_agent'

if CURRENT_ENV in ['test', 'uat']:
    ThermoelectricServerUrl = 'http://root@mllo1368252.bohrium.tech:50001/sse'
else:
    ThermoelectricServerUrl = 'https://thermoelectricmcp000-uuid1750905361.appspace.bohrium.com/sse?token=f195408805934dab9313de6fb46f8767'
