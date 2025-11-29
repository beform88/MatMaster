'''
Author: error: error: git config user.name & please set dead value or install git && error: git config user.email & please set dead value or install git & please set dead value or install git
Date: 2025-11-29 11:53:56
LastEditors: error: error: git config user.name & please set dead value or install git && error: git config user.email & please set dead value or install git & please set dead value or install git
LastEditTime: 2025-11-29 20:56:58
FilePath: \MatMaster\agents\matmaster_agent\sub_agents\XRD_agent\constant.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
import copy

from agents.matmaster_agent.constant import CURRENT_ENV, BohriumStorge

XRD_AGENT_NAME = 'xrd_agent'
if CURRENT_ENV in ['test', 'uat']:
    XRD_MCP_SERVER_URL = 'http://62.234.182.84:50001/sse'
    # NMR_MCP_SERVER_URL = 'https://nmr-uuid1751618147.app-space.dplink.cc/sse?token=beab553bf78b4c53a7490531d14492c4'
else:
    XRD_MCP_SERVER_URL = 'http://62.234.182.84:50001/sse'
    # NMR_MCP_SERVER_URL = 'https://nmr-uuid1751618147.app-space.dplink.cc/sse?token=beab553bf78b4c53a7490531d14492c4'

XRD_BOHRIUM_STORAGE = copy.deepcopy(BohriumStorge)
