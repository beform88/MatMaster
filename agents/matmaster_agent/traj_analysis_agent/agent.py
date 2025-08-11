from dp.agent.adapter.adk import CalculationMCPToolset
from google.adk.agents import BaseAgent
from google.adk.tools.mcp_tool.mcp_session_manager import SseServerParams

from agents.matmaster_agent.base_agents.job_agent import CalculationMCPLlmAgent
from agents.matmaster_agent.constant import BohriumStorge
from agents.matmaster_agent.traj_analysis_agent.constant import (
    TrajAnalysisAgentName,
    TrajAnalysisMCPServerUrl,
)

toolset = CalculationMCPToolset(
    connection_params=SseServerParams(
        url=TrajAnalysisMCPServerUrl
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
        tools=[toolset]
    )
