import asyncio
import os
import sys
import time
import uuid
from typing import Optional, Any

from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from opik import Opik
from opik.evaluation import evaluate
from opik.evaluation.metrics import base_metric, score_result

from agents.matmaster_agent.agent import root_agent
from agents.matmaster_agent.constant import MATMASTER_AGENT_NAME
from agents.matmaster_agent.utils.event_utils import is_function_call
from agents.matmaster_agent.utils.helper_func import is_same_function_call

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 1. opik setup
# use this if opik is running in local
load_dotenv()
client = Opik()
dataset = client.get_dataset(name="MatMaster SubAgent")

# 2. adk setup
# --- Runner ---
session_service = InMemorySessionService()
# Key Concept: Runner orchestrates the agent execution loop.
runner = Runner(
    agent=root_agent,  # The agent we want to run
    app_name=MATMASTER_AGENT_NAME,  # Associates runs with our app
    session_service=session_service  # Uses our session manager
)

# 3. metrics setup
metrics_evaluate_model = "azure/gpt-4o"


class TransferToAgentQuality(base_metric.BaseMetric):
    """
    A metric that evaluates whether the output contains markdown formatted data.
    This metric checks if the actual output matches the expected markdown formatted data.
    It returns a score of 1 if the output matches the expected format, and 0 otherwise.
    Args:
        name: The name of the metric.
        ignore_whitespace: Whether to ignore whitespace differences when comparing output.
        track: Whether to track the metric. Defaults to True.
        project_name: Optional project name to track the metric in.
    """

    def __init__(
            self,
            name: str = "transfer_to_agent_quality",
            model: Optional[str] = "azure/gpt-4o",
            ignore_whitespace: bool = True,
            track: bool = True,
            project_name: Optional[str] = None,
    ):
        self.model = model
        self.ignore_whitespace = ignore_whitespace
        super().__init__(name=name, track=track, project_name=project_name)

    def score(
            self,
            output: str,
            function_call: dict,
            expected_function_call: dict,
            **kwargs: Any,
    ) -> score_result.ScoreResult:
        """
        Calculate the markdown data match score using LLM.
        Args:
            output: The actual output to evaluate.
            **kwargs: Additional keyword arguments that are ignored.
        Returns:
            score_result.ScoreResult: A ScoreResult object with a value of 1.0 if the output
                matches the expected format, 0.0 otherwise, along with the reason for the verdict.
        """
        try:

            if is_same_function_call(function_call, expected_function_call):
                return score_result.ScoreResult(
                    name=self.name,
                    value=1
                )
            else:
                return score_result.ScoreResult(
                    name=self.name,
                    value=0,
                    reason=f"current_function_call: {function_call},"
                           f"expected_function_call: {expected_function_call}"
                )
        except Exception as e:
            print(e)
            return score_result.ScoreResult(
                name=self.name,
                value=0,
                reason=f"Scoring error: {str(e)}"
            )


metrics = [TransferToAgentQuality(model=metrics_evaluate_model)]


def evaluation_task(dataset_item):
    # Create the specific session where the conversation will happen
    session = asyncio.run(session_service.create_session(
        app_name=MATMASTER_AGENT_NAME,
        user_id="evaluator",
        session_id=uuid.uuid4().hex
    ))

    print(dataset_item['input'])
    user_query = dataset_item['input']['contents'][0]['parts'][0]['text']
    expected_function_calls = {
        "function_name": dataset_item["expected_output"]["content"]["parts"][0]["function_call"]["name"],
        "function_args": dataset_item["expected_output"]["content"]["parts"][0]["function_call"]["args"]
    }
    content = types.Content(role='user', parts=[types.Part(text=user_query)])

    events = []
    function_calls = {}

    for event in runner.run(user_id=session.user_id, session_id=session.id, new_message=content):
        events.append(event)
        if is_function_call(event):
            function_calls = {
                "function_name": event.content.parts[0].function_call.name,
                "function_args": event.content.parts[0].function_call.args
            }
            break

    output = events[-1].content.parts[0].text
    result = {
        "input": user_query,
        "output": output,
        "function_call": function_calls,
        "expected_function_call": expected_function_calls,
        "context": []
    }
    return result


eval_results = evaluate(
    experiment_name="transfer_to_agent" + time.strftime("_%Y%m%d_%H%M%S"),
    dataset=dataset,
    task=evaluation_task,
    scoring_metrics=metrics,
)
