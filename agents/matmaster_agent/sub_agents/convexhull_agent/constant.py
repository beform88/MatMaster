from agents.matmaster_agent.constant import CURRENT_ENV

ConvexHullAgentName = 'convexhull_agent'
if CURRENT_ENV in ['test', 'uat']:
    ConvexHullServerUrl = 'http://root@mllo1368252.bohrium.tech:50004/sse'
else:
    ConvexHullServerUrl = 'https://superconductor-ambient-010-uuid1750845273.app-space.dplink.cc/sse?token=48f4f42c8a14469b9729c98b4ce7f8f6'
