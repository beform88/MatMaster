import time

from opik import evaluate, Opik

from evaluate.base import evaluation_task
from evaluate.constant import TRANSFER_TO_AGENT_QUALITY, MATMASTER_SUBAGENT, MULTI_OPTION_QUALITY, \
    MATMASTER_MULTI_OPTION
from evaluate.multi_options_quality import MultiOptionQuality
from evaluate.transfer_to_agent_quality import TransferToAgentQuality

# transfer_to_agent_quality
evaluate(
    experiment_name=TRANSFER_TO_AGENT_QUALITY + time.strftime("_%Y%m%d_%H%M%S"),
    dataset=Opik().get_dataset(name=MATMASTER_SUBAGENT),
    task=evaluation_task,
    scoring_metrics=[TransferToAgentQuality(model="azure/gpt-4o")],
)

# multi_options_quality
evaluate(
    experiment_name=MULTI_OPTION_QUALITY + time.strftime("_%Y%m%d_%H%M%S"),
    dataset=Opik().get_dataset(name=MATMASTER_MULTI_OPTION),
    task=evaluation_task,
    scoring_metrics=[MultiOptionQuality(model="azure/gpt-4o")],
)
