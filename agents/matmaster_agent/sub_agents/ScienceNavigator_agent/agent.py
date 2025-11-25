import asyncio
import os
import traceback

from dotenv import load_dotenv
from dp.agent.adapter.adk import CalculationMCPToolset
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPServerParams, SseServerParams

from agents.matmaster_agent.constant import MATMASTER_AGENT_NAME
from agents.matmaster_agent.job_agents.agent import BaseAsyncJobAgent
from agents.matmaster_agent.llm_config import LLMConfig
from agents.matmaster_agent.logger import matmodeler_logging_handler
from agents.matmaster_agent.sub_agents.ScienceNavigator_agent.constant import (
    SCIENCE_NAVIGATOR_AGENT_NAME,
    SCIENCE_NAVIGATOR_MCP_SERVER_URL
)
from agents.matmaster_agent.sub_agents.ScienceNavigator_agent.prompt import (
    SCIENCE_NAVIGATOR_AGENT_DESCRIPTION,
    SCIENCE_NAVIGATOR_AGENT_INSTRUCTION,
)

science_navigator_toolset = McpToolset(
    connection_params=SseServerParams(url=SCIENCE_NAVIGATOR_MCP_SERVER_URL)
)


class ScienceNavigatorAgent(BaseAsyncJobAgent):
    def __init__(self, llm_config: LLMConfig):
        super().__init__(
            name=SCIENCE_NAVIGATOR_AGENT_NAME,
            tools=[science_navigator_toolset],
            model=llm_config.default_litellm_model,
            description=SCIENCE_NAVIGATOR_AGENT_DESCRIPTION,
            instruction=SCIENCE_NAVIGATOR_AGENT_INSTRUCTION,
            dflow_flag=False,
            supervisor_agent=MATMASTER_AGENT_NAME,
        )


def init_science_navigator_agent(llm_config):
    return ScienceNavigatorAgent(llm_config)