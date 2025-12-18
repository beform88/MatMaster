from agents.matmaster_agent.constant import CURRENT_ENV

VisualizerAgentName = 'visualizer_agent'

if CURRENT_ENV in ['test', 'uat']:
    VisualizerServerUrl = 'http://qpus1389933.bohrium.tech:50005/mcp'
else:
    # VisualizerServerUrl = 'https://visualization-agent-uuid1762946293.appspace.bohrium.com/sse?token=0b925beda7e44f66b69047319e87967d'
    VisualizerServerUrl = 'http://qpus1389933.bohrium.tech:50002/mcp'
