from opik.evaluation import evaluate_threads
from opik.evaluation.metrics import ConversationalCoherenceMetric, UserFrustrationMetric, SessionCompletenessQuality
from opik.evaluation.metrics.conversation.conversation_thread_metric import ConversationThreadMetric
from opik.evaluation.models import base_model, models_factory
from opik.evaluation.metrics.conversation import types as conversation_types
from opik.evaluation.metrics import score_result
from google.genai import types
from litellm import completion
from dotenv import load_dotenv
import json

load_dotenv()

metrics_evalute_model = "azure/gpt-4o"

# Initialize the evaluation metrics

class BorhriumJobSubmitSuccessMetric(ConversationThreadMetric):
    def __init__(self, model: str, name: str = "borhrium_job_submit_success"):
        self._init_model(model)
        super().__init__(name=name)
        
    def _init_model(self, model: str):
        self._model = model
        
    def _get_template(self):
        return """
        You are a borhrium job submit success detector. Please determine if the following output is a success.

        Definition of success:
        - The job is submitted successfully(there is a valid link to https://bohrium.test.dp.tech or (https://bohrium.dp.tech linking to the job detail).

        Output:
        {conversation}

        Format your response as JSON:
        {{
            "score": int,  # 1 if success, 0 otherwise
            "reason": str    # Detailed explanation
        }}

        Notice: The output should be in the format of JSON, DO NOT wrap the output with any other characters.
        """

    def get_prompt(self, conversation: conversation_types.Conversation) -> str:
        return self._get_template().format(conversation=conversation)
   
    def score(self, conversation: conversation_types.Conversation, **kwargs) -> score_result.ScoreResult:
        try:
            if len(conversation) == 0:
                raise ValueError("Conversation is empty")
            
            
            prompt = self.get_prompt(conversation=conversation)
            
            response = completion(
                model=self._model,
                messages=[{"role": "user", "content": prompt}],
            )
            print(f"response: {response}")
            
            # Parse the response
            # TODO 参考 opik 官方例子用更 safe 的 json 解析方式
            result: dict = json.loads(response.choices[0].message.content)
            score = int(result.get("score", 0))
            reason = str(result.get("reason", "No explanation provided"))
            print(result)
           
            return score_result.ScoreResult(
                name=self.name,
                value=score,
                reason=reason
            )
        except Exception as e:
            print(f"Failed to calculate borhrium job submit success: {e}")
            return score_result.ScoreResult(
                name=self.name,
                value=0,
                reason=f"Scoring error: {str(e)}"
            )

conversation_coherence_metric = ConversationalCoherenceMetric(model=metrics_evalute_model)
user_frustration_metric = UserFrustrationMetric(model=metrics_evalute_model)
session_completeness_quality_metric = SessionCompletenessQuality(model=metrics_evalute_model)
borhrium_job_submit_success_metric = BorhriumJobSubmitSuccessMetric(model=metrics_evalute_model)


## parse input and output for metrics
def trace_input_transform(x):
    print(f"input x.keys(): {x.keys()}")
    print(f"input x: {x}")
    return x['parts'][0]['text']

def trace_output_transform(x):
    print(f"output x.keys(): {x.keys()}")
    print(f"output x: {x}")
    return x['content']['parts'][0]['text']


# Run the threads evaluation
results = evaluate_threads(
    project_name="test",
    # filter_string='id = "8f17d4f1-8166-460a-8c6b-22f0e7713dda" AND status = "inactive"',
    filter_string='tags contains "bohrium_job"',
    eval_project_name="lp_threads_evaluation",
    metrics=[
        # conversation_coherence_metric,
        # user_frustration_metric,
        session_completeness_quality_metric,
        borhrium_job_submit_success_metric,
    ],
    trace_input_transform=trace_input_transform,
    trace_output_transform=trace_output_transform,
)
print(results)