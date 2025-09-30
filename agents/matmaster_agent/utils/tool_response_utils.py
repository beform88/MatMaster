from agents.matmaster_agent.utils.helper_func import is_json


def check_valid_tool_response(tool_response):
    return (
        tool_response
        and tool_response.content
        and tool_response.content[0].text
        and is_json(tool_response.content[0].text)
    )
