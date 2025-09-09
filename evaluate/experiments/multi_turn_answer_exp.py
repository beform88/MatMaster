import time

from opik import evaluate, Opik
from opik.evaluation.metrics import AnswerRelevance

from evaluate.base import multi_turn_evaluation_task
from evaluate.constant import MATMASTER_MULTI_TURN_ANSWER_QUALITY

# multi_turn_answer_quality
evaluate(
    experiment_name=MATMASTER_MULTI_TURN_ANSWER_QUALITY + time.strftime("_%Y%m%d_%H%M%S"),
    dataset=Opik().get_dataset(name=MATMASTER_MULTI_TURN_ANSWER_QUALITY),
    task=multi_turn_evaluation_task,
    scoring_metrics=[
        AnswerRelevance(name=MATMASTER_MULTI_TURN_ANSWER_QUALITY, model="azure/gpt-4o", require_context=False)],
)
