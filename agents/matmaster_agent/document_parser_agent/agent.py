from dp.agent.adapter.adk import CalculationMCPToolset
from google.adk.agents import BaseAgent
from google.adk.tools.mcp_tool.mcp_session_manager import SseServerParams

from agents.matmaster_agent.constant import MATMASTER_AGENT_NAME, BohriumStorge

from ..base_agents.sync_agent import SyncMCPLlmAgent
from .callback import validate_document_url
from .constant import DocumentParserAgentName, DocumentParserServerUrl
from .prompt import DocumentParserAgentDescription, DocumentParserAgentInstruction

sse_params = SseServerParams(url=DocumentParserServerUrl)
toolset = CalculationMCPToolset(connection_params=sse_params, storage=BohriumStorge)


class DocumentParserAgent(SyncMCPLlmAgent):
    def __init__(self, llm_config):
        super().__init__(
            model=llm_config.gpt_5_chat,
            name=DocumentParserAgentName,
            description=DocumentParserAgentDescription,
            instruction=DocumentParserAgentInstruction,
            tools=[toolset],
            supervisor_agent=MATMASTER_AGENT_NAME,
            after_model_callback=validate_document_url,
        )


def init_document_parser_agent(llm_config) -> BaseAgent:
    """Initialize Document Parser Agent"""
    return DocumentParserAgent(llm_config)
