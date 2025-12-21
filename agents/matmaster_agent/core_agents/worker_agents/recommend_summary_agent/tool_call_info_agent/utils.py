import logging

from deepmerge import always_merger

from agents.matmaster_agent.constant import MATMASTER_AGENT_NAME
from agents.matmaster_agent.logger import PrefixFilter

logger = logging.getLogger(__name__)
logger.addFilter(PrefixFilter(MATMASTER_AGENT_NAME))
logger.setLevel(logging.INFO)


def update_tool_call_info_with_function_declarations(
    tool_call_info, current_function_declaration
):
    required_params = []
    if current_function_declaration[0]['parameters'].get('required'):
        required_params = current_function_declaration[0]['parameters']['required']
    logger.info(f'required_params = {required_params}')

    for param in required_params:
        if (
            param in tool_call_info['tool_args'].keys()
            or param in tool_call_info['missing_tool_args']
        ):
            continue
        else:
            tool_call_info['missing_tool_args'].append(param)

    return tool_call_info


def update_tool_call_info_with_recommend_params(tool_call_info, recommend_params):
    tool_call_info['tool_args'] = always_merger.merge(
        tool_call_info['tool_args'], recommend_params
    )
    for arg in tool_call_info['missing_tool_args']:
        if arg in tool_call_info['tool_args'].keys():
            tool_call_info['missing_tool_args'].remove(arg)

    return tool_call_info
