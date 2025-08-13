from agents.matmaster_agent.constant import CURRENT_ENV

ThermoelectricAgentName = "thermoelectric_agent"

if CURRENT_ENV in ["test", "uat"]:
   ThermoelectricServerUrl="http://root@mllo1368252.bohrium.tech:50001/sse"
else:
   ThermoelectricServerUrl="https://a4d3af69a34ee0822adcbfc50bf1ded5.app-space.dplink.cc/sse?token=380d235147764ba1ba112b3f3c283d8b"

	
