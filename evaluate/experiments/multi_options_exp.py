import time

from opik import evaluate, Opik

from evaluate.base import evaluation_task
from evaluate.constant import MULTI_OPTION_QUALITY, \
    MATMASTER_MULTI_OPTION
from evaluate.metric.multi_options_quality import MultiOptionQuality

# multi_options_quality
evaluate(
    experiment_name=MULTI_OPTION_QUALITY + time.strftime('_%Y%m%d_%H%M%S'),
    dataset=Opik().get_dataset(name=MATMASTER_MULTI_OPTION),
    task=evaluation_task,
    scoring_metrics=[MultiOptionQuality(model='azure/gpt-4o')],
)
