from agents.matmaster_agent.constant import CURRENT_ENV


SuperconductorAgentName = "superconductor_agent"
if CURRENT_ENV in ["test", "uat"]:
   SuperconductorServerUrl="http://root@mllo1368252.bohrium.tech:50002/sse"
else:
   SuperconductorServerUrl="https://45e81409831b77407fbc22afc09f0d78.app-space.dplink.cc/sse?token=53f7b7c134ed48e0b00823b6401f0925"

	
