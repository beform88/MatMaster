from agents.matmaster_agent.constant import CURRENT_ENV


SuperconductorAgentName = "superconductor_agent"
if CURRENT_ENV in ["test", "uat"]:
   SuperconductorServerUrl="http://root@mllo1368252.bohrium.tech:50002/sse"
else:
   SuperconductorServerUrl="https://6de4bfe9504589a457d6e92fae4f9613.app-space.dplink.cc/sse?token=92019901c5e04d12b35ebbfb6276e34e"

	
