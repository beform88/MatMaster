import copy

from agents.matmaster_agent.constant import CURRENT_ENV, BohriumStorge

Physical_Adsorption_AGENT_NAME = 'physical_adsorption_agent'
if CURRENT_ENV in ['test', 'uat']:
    Physical_Adsorption_MCP_SERVER_URL = (
        'http://root@pkfz1410356.bohrium.tech:50003/sse'
    )
else:
    Physical_Adsorption_MCP_SERVER_URL = (
        'http://root@pkfz1410356.bohrium.tech:50003/sse'
    )

Physical_Adsorption_BOHRIUM_STORAGE = copy.deepcopy(BohriumStorge)