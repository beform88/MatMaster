import copy

from agents.matmaster_agent.constant import CURRENT_ENV, BohriumStorge

NMR_AGENT_NAME = 'nmr_agent'
if CURRENT_ENV in ['test', 'uat']:
    NMR_MCP_SERVER_URL = 'http://aubn1408899.bohrium.tech:50001/sse'
    # NMR_MCP_SERVER_URL = 'https://nmr-uuid1751618147.app-space.dplink.cc/sse?token=beab553bf78b4c53a7490531d14492c4'
else:
    NMR_MCP_SERVER_URL = 'http://aubn1408899.bohrium.tech:50001/sse'
    # NMR_MCP_SERVER_URL = 'https://nmr-uuid1751618147.app-space.dplink.cc/sse?token=beab553bf78b4c53a7490531d14492c4'

NMR_BOHRIUM_STORAGE = copy.deepcopy(BohriumStorge)
