from agents.matmaster_agent.constant import CURRENT_ENV

ThermoelectricAgentName = "thermoelectric_agent"

if CURRENT_ENV in ["test", "uat"]:
   ThermoelectricServerUrl="http://root@mllo1368252.bohrium.tech:50001/sse"
else:
   ThermoelectricServerUrl="https://bbc92a647199b832ec90d7cf57074e9e.app-space.dplink.cc/sse?token=58f898ea2e75419a957c1eb9c76c1ece"

	
