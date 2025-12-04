from agents.matmaster_agent.base_agents.public_agent import (
    BaseSyncAgentWithToolValidator,
)
from agents.matmaster_agent.llm_config import LLMConfig
from agents.matmaster_agent.sub_agents.built_in_agent.file_parse_agent.constant import (
    FILE_PARSE_AGENT_NAME,
)
from agents.matmaster_agent.sub_agents.built_in_agent.file_parse_agent.tools import (
    file_parse,
)
from agents.matmaster_agent.sub_agents.built_in_agent.file_parse_agent.prompt import (
    FileParseAgentInstruction,
)

class FileParseAgent(BaseSyncAgentWithToolValidator):
    def __init__(self, llm_config: LLMConfig):
        super().__init__(
            model=llm_config.default_litellm_model,
            name=FILE_PARSE_AGENT_NAME,
            description='',
            instruction=FileParseAgentInstruction,
            tools=[file_parse],
        )


def init_tool_agent(llm_config) -> BaseSyncAgentWithToolValidator:
    return FileParseAgent(llm_config)
