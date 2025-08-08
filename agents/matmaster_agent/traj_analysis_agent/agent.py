import json
from typing import Any, Dict

from dp.agent.adapter.adk import CalculationMCPToolset
from google.adk.agents import BaseAgent
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.mcp_tool.mcp_session_manager import SseServerParams
from google.adk.tools.tool_context import ToolContext
from mcp.types import CallToolResult

from agents.matmaster_agent.base_agents.job_agent import CalculationMCPLlmAgent
from agents.matmaster_agent.constant import BohriumStorge
from agents.matmaster_agent.logger import logger
from agents.matmaster_agent.traj_analysis_agent.constant import (
    TrajAnalysisAgentName,
)
from agents.matmaster_agent.utils.helper_func import is_json


async def before_tool_callback(tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext):
    agent_name = tool_context.agent_name
    tool_name = tool.name
    print(f"[Callback] Before tool call for tool '{tool_name}' in agent '{agent_name}'")
    print(f"[Callback] Args: {args}")


async def after_tool_callback(tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext,
                              tool_response: CallToolResult):
    """轨迹处理工具的后处理，将base64图像上传至OSS并生成Markdown格式"""
    tool_info = {
        "after": {
            'tool_name': tool.name,
            'tool_args': args,
            'tool_response': tool_response.content[0].text if (tool_response and len(tool_response.content)) else None
        }
    }

    # 检查是否有有效的图像数据
    if not (tool_response and
            tool_response.content and
            tool_response.content[0].text and
            is_json(tool_response.content[0].text) and
            json.loads(tool_response.content[0].text).get('plot', None) is not None):
        print("[Callback] Tool response is not JSON")
        return None

    try:
        markdown_image = f"![traj_png]({json.loads(tool_response.content[0].text)['plot']})"
        tool_info['after']['tool_response'] = markdown_image
        return markdown_image
    except Exception as e:
        logger.error(f"Failed to process traj image: {str(e)}")
    return None


toolset = CalculationMCPToolset(
    connection_params=SseServerParams(
        url="https://traj-analysis-mcp-uuid1753018121.app-space.dplink.cc/sse?"
            "token=5e75ed9197b741dcb267612ca20a096d"
    ),
    storage=BohriumStorge
)


def init_traj_analysis_agent(llm_config) -> BaseAgent:
    return CalculationMCPLlmAgent(
        model=llm_config.gpt_4o,
        name=TrajAnalysisAgentName,
        description='An agent designed to perform trajectory analysis, including calculations like '
                    'Solvation Structure Analysis, Mean Squared Displacement (MSD) and Radial Distribution Function (RDF), '
                    'along with generating corresponding visualizations.',
        instruction="""
        This agent specializes in analyzing molecular dynamics (MD) simulation trajectories,
        with the following key functionalities:
        Solvation Structure Analysis:
        1. analyse SSIP/CIP/AGG ratios for electrolyte
        2. calculate coordination number of solvents

        Mean Squared Displacement (MSD) Analysis:
        Calculates and plots MSD curves for the system
        Supports exporting MSD calculation results as data files
        Allows computation for specific atom groups (requires user-provided atom indices/types)
        If no atoms are specified, calculates MSD for all atoms by default

        Radial Distribution Function (RDF) Analysis:
        Computes and plots RDF curves for different atom pairs
        Supports specifying central and neighboring atom types
        If no atom types are specified, calculates RDF for all atom pairs by default

        Visualization Output:
        Prioritizes displaying analysis plots in embedded Markdown format
        Also provides downloadable image file links
        """,
        tools=[toolset],
        before_tool_callback=before_tool_callback,
        after_tool_callback=after_tool_callback
    )
