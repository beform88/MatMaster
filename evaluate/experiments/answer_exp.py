import time

from opik import evaluate, Opik
from opik.evaluation.metrics import AnswerRelevance

from evaluate.base import evaluation_task
from evaluate.constant import MATMASTER_PLAN_QUALITY

# answer_quality
evaluate(
    experiment_name=MATMASTER_PLAN_QUALITY + time.strftime("_%Y%m%d_%H%M%S"),
    dataset=Opik().get_dataset(name=MATMASTER_PLAN_QUALITY),
    task=evaluation_task,
    scoring_metrics=[AnswerRelevance(name=MATMASTER_PLAN_QUALITY, model="azure/gpt-4o", require_context=False)],
)
