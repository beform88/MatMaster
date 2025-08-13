from agents.matmaster_agent.constant import CURRENT_ENV


SuperconductorAgentName = "superconductor_agent"
if CURRENT_ENV in ["test", "uat"]:
   SuperconductorServerUrl="http://root@mllo1368252.bohrium.tech:50002/sse"
else:
   SuperconductorServerUrl="https://c4819d06b0ca810d38506453cfaae9d8.app-space.dplink.cc/sse?token=f9e2ba41ee0c4165a9bc0c7d08227bae"

	
