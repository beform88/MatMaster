import time

from opik import Opik
from opik import evaluate
from opik.evaluation.metrics import AnswerRelevance

from evaluate.base.evaluation import evaluation_task
from evaluate.utils import load_dataset_json

MATMASTER_ANSWER_QUALITY = 'MatMaster-Answer-Quality'

# Get or create a dataset
client = Opik()

dataset = client.get_or_create_dataset(name=MATMASTER_ANSWER_QUALITY)
dataset.clear()
dataset_json = load_dataset_json(__file__.replace('.py', '.json'))
dataset.insert_from_json(dataset_json)

evaluate(
    experiment_name=MATMASTER_ANSWER_QUALITY + time.strftime('_%Y%m%d_%H%M%S'),
    dataset=dataset,
    task=evaluation_task,
    scoring_metrics=[AnswerRelevance(name=MATMASTER_ANSWER_QUALITY, model='azure/gpt-4o', require_context=False)],
)
