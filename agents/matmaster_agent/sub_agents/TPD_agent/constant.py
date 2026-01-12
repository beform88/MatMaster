import copy

from agents.matmaster_agent.constant import CURRENT_ENV, BohriumStorge

TPD_AGENT_NAME = 'tpd_agent'
if CURRENT_ENV in ['test', 'uat']:
    TPD_MCP_SERVER_URL = 'http://root@pkfz1410356.bohrium.tech:50004/sse'
    # NMR_MCP_SERVER_URL = 'https://nmr-uuid1751618147.app-space.dplink.cc/sse?token=beab553bf78b4c53a7490531d14492c4'
else:
    TPD_MCP_SERVER_URL = 'http://root@pkfz1410356.bohrium.tech:50004/sse'
    # NMR_MCP_SERVER_URL = 'https://nmr-uuid1751618147.app-space.dplink.cc/sse?token=beab553bf78b4c53a7490531d14492c4'

TPD_BOHRIUM_STORAGE = copy.deepcopy(BohriumStorge)
