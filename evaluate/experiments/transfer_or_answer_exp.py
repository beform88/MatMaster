import time

from opik import evaluate, Opik

from evaluate.base import evaluation_task
from evaluate.constant import MATMASTER_TRANSFER_OR_ANSWER_QUALITY
from evaluate.metric.transfer_or_answer_quality import TransferOrAnswerQuality

# transfer_and_answer_quality
evaluate(
    experiment_name=MATMASTER_TRANSFER_OR_ANSWER_QUALITY + time.strftime("_%Y%m%d_%H%M%S"),
    dataset=Opik().get_dataset(name=MATMASTER_TRANSFER_OR_ANSWER_QUALITY),
    task=evaluation_task,
    scoring_metrics=[TransferOrAnswerQuality(model="azure/gpt-4o")],
)
