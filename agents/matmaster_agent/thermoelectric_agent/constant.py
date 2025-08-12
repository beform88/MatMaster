from agents.matmaster_agent.constant import CURRENT_ENV

ThermoelectricAgentName = "thermoelectric_agent"

if CURRENT_ENV in ["test", "uat"]:
   ThermoelectricServerUrl="http://root@mllo1368252.bohrium.tech:50001/sse"
else:
   ThermoelectricServerUrl="https://thermoelectricmcp000-uuid1750905361.app-space.dplink.cc/sse?token=02ad1b7102c14734acc16731a017ada2"

	
