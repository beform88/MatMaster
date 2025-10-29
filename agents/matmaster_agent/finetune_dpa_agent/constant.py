from agents.matmaster_agent.constant import CURRENT_ENV

FinetuneDPAAgentName = 'finetune_dpa_agent'

if CURRENT_ENV in ['test', 'uat']:
    FinetuneDPAServerUrl = 'http://root@mllo1368252.bohrium.tech:50003/sse'
else:
    FinetuneDPAServerUrl = 'https://b3af1c7992383988a4bd73c7e9f14759.app-space.dplink.cc/sse?token=869418403c974181be9b051a2fe1dc96'
