from agents.matmaster_agent.constant import CURRENT_ENV

ThermoelectricAgentName = "thermoelectric_agent"

if CURRENT_ENV in ["test", "uat"]:
   ThermoelectricServerUrl="http://root@mllo1368252.bohrium.tech:50001/sse"
else:
   ThermoelectricServerUrl="https://thermoelectricmcp000-uuid1750905361.app-space.dplink.cc/sse?token=5d7a7dfa9657494d9122808db0c147bd"

	
