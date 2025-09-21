import time

from opik import Opik, evaluate

from evaluate.base.evaluation import evaluation_task
from evaluate.constant import MATMASTER_SUBAGENT, TRANSFER_TO_AGENT_QUALITY
from evaluate.metric.transfer_to_agent_quality import TransferToAgentQuality

# transfer_to_agent_quality
evaluate(
    experiment_name=TRANSFER_TO_AGENT_QUALITY + time.strftime('_%Y%m%d_%H%M%S'),
    dataset=Opik().get_dataset(name=MATMASTER_SUBAGENT),
    task=evaluation_task,
    scoring_metrics=[TransferToAgentQuality(model='azure/gpt-4o')],
)
