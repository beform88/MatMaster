import asyncio
import uuid

from google.adk import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from agents.matmaster_agent.agent import root_agent
from agents.matmaster_agent.constant import MATMASTER_AGENT_NAME
from agents.matmaster_agent.utils.event_utils import is_function_call


def evaluation_task(dataset_item):
    session_service = InMemorySessionService()
    runner = Runner(agent=root_agent, app_name=MATMASTER_AGENT_NAME, session_service=session_service)
    session = asyncio.run(session_service.create_session(
        app_name=MATMASTER_AGENT_NAME,
        user_id="evaluator",
        session_id=uuid.uuid4().hex
    ))

    expected_function_call = {}
    if dataset_item["input"].get("contents", None):
        user_query = dataset_item['input']['contents'][0]['parts'][0]['text']
        for part in dataset_item['expected_output']['content']['parts']:
            if part.get("function_call"):
                expected_function_call = {
                    "function_name": part["function_call"]["name"],
                    "function_args": part["function_call"]["args"]
                }
    else:
        user_query = dataset_item["input"]["parts"][0]['text']
        if dataset_item["expected_output"]["content"]["parts"][0].get("function_call"):
            expected_function_call = {
                "function_name": dataset_item["expected_output"]["content"]["parts"][0]["function_call"]["name"],
                "function_args": dataset_item["expected_output"]["content"]["parts"][0]["function_call"]["args"]
            }

    content = types.Content(role='user', parts=[types.Part(text=user_query)])

    events = []
    function_call = {}
    for event in runner.run(user_id=session.user_id, session_id=session.id, new_message=content):
        events.append(event)
        if is_function_call(event):
            function_call = {
                "function_name": event.content.parts[0].function_call.name,
                "function_args": event.content.parts[0].function_call.args
            }
            break

    output = events[-1].content.parts[0].text
    result = {
        "input": user_query,
        "output": output,
        "function_call": function_call,
        "expected_function_call": expected_function_call,
        "context": []
    }
    return result


def multi_turn_evaluation_task(dataset_item):
    session_service = InMemorySessionService()
    runner = Runner(agent=root_agent, app_name=MATMASTER_AGENT_NAME, session_service=session_service)
    session = asyncio.run(session_service.create_session(
        app_name=MATMASTER_AGENT_NAME,
        user_id="evaluator",
        session_id=uuid.uuid4().hex
    ))

    expected_function_call = {}
    turn_index = 2
    if dataset_item["input"].get("contents", None):
        user_query = ""
        for input_part in dataset_item['input']['contents'][:turn_index]:
            input_part_text = input_part["parts"][0]["text"]
            input_part_role = input_part["role"]
            user_query += f"For context: [{input_part_role}]\n{input_part_text}\n"
            user_query += "---------------------\n"
        user_query += dataset_item['input']['contents'][turn_index]["parts"][0]["text"]
    else:
        user_query = dataset_item["input"]["parts"][0]['text']
        if dataset_item["expected_output"]["content"]["parts"][0].get("function_call"):
            expected_function_call = {
                "function_name": dataset_item["expected_output"]["content"]["parts"][0]["function_call"]["name"],
                "function_args": dataset_item["expected_output"]["content"]["parts"][0]["function_call"]["args"]
            }

    content = types.Content(role='user', parts=[types.Part(text=user_query)])

    events = []
    function_call = {}
    for event in runner.run(user_id=session.user_id, session_id=session.id, new_message=content):
        events.append(event)

    output = events[-1].content.parts[0].text
    result = {
        "input": user_query,
        "output": output,
        "function_call": function_call,
        "expected_function_call": expected_function_call,
        "context": []
    }
    return result
