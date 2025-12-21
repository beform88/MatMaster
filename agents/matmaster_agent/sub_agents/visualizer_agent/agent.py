from dp.agent.adapter.adk import CalculationMCPToolset
from google.adk.agents import BaseAgent
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPServerParams

from agents.matmaster_agent.constant import MATMASTER_AGENT_NAME, BohriumStorge
from agents.matmaster_agent.llm_config import LLMConfig

from ...core_agents.worker_agents.sync_agent import BaseSyncAgentWithToolValidator
from .callback import validate_visualization_url
from .constant import VisualizerAgentName, VisualizerServerUrl
from .prompt import VisualizerAgentDescription, VisualizerAgentInstruction

MCP_params = StreamableHTTPServerParams(url=VisualizerServerUrl)
visualizer_toolset = CalculationMCPToolset(
    connection_params=MCP_params, storage=BohriumStorge
)


class VisualizerAgent(BaseSyncAgentWithToolValidator):
    def __init__(self, llm_config: LLMConfig):
        super().__init__(
            model=llm_config.default_litellm_model,
            name=VisualizerAgentName,
            description=VisualizerAgentDescription,
            instruction=VisualizerAgentInstruction,
            tools=[visualizer_toolset],
            supervisor_agent=MATMASTER_AGENT_NAME,
            after_model_callback=validate_visualization_url,
            render_tool_response=False,
        )


def init_visualizer_agent(llm_config) -> BaseAgent:
    """Initialize Visualizer Agent"""
    return VisualizerAgent(llm_config)
