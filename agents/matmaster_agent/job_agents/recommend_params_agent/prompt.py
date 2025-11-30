from agents.matmaster_agent.prompt import HUMAN_FRIENDLY_FORMAT_REQUIREMENT


def gen_recommend_params_agent_instruction():
    return f"""
Convert the recommended parameters into a user-friendly format for a tool invocation.

- The output language must be {{target_language}}.

## FORMAT INSTRUCTIONS:
{HUMAN_FRIENDLY_FORMAT_REQUIREMENT}

Critical Instructions:
- If the input parameter is a **complete HTTP or HTTPS URL**, use it directly as the parameter.
- Present the information in a clear, readable style, such as a list or natural paragraphs.
- Do not end with any question or prompt for user action.
"""
