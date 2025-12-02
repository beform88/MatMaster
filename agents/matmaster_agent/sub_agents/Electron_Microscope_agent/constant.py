import copy

from agents.matmaster_agent.constant import CURRENT_ENV, BohriumStorge

Electron_Microscope_AGENT_NAME = 'electron_microscope_agent'
if CURRENT_ENV in ['test', 'uat']:
    Electron_Microscope_MCP_SERVER_URL = (
        'http://root@pkfz1410356.bohrium.tech:50002/sse'
    )
    # NMR_MCP_SERVER_URL = 'https://nmr-uuid1751618147.app-space.dplink.cc/sse?token=beab553bf78b4c53a7490531d14492c4'
else:
    Electron_Microscope_MCP_SERVER_URL = (
        'http://root@pkfz1410356.bohrium.tech:50002/sse'
    )
    # NMR_MCP_SERVER_URL = 'https://nmr-uuid1751618147.app-space.dplink.cc/sse?token=beab553bf78b4c53a7490531d14492c4'

Electron_Microscope_BOHRIUM_STORAGE = copy.deepcopy(BohriumStorge)
