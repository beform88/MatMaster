from google.adk.models import LlmResponse


def has_function_call(llm_response: LlmResponse) -> bool:
    for part in llm_response.content.parts:
        if part.function_call:
            return True
    return False
