import time

from opik import evaluate, Opik
from opik.evaluation.metrics import AnswerRelevance

from evaluate.base import evaluation_task, multi_turn_evaluation_task
from evaluate.constant import TRANSFER_TO_AGENT_QUALITY, MATMASTER_SUBAGENT, MULTI_OPTION_QUALITY, \
    MATMASTER_MULTI_OPTION, MATMASTER_PLAN_QUALITY, MATMASTER_MULTI_TURN_ANSWER_QUALITY, \
    MATMASTER_TRANSFER_OR_ANSWER_QUALITY
from evaluate.multi_options_quality import MultiOptionQuality
from evaluate.transfer_or_answer_quality import TransferOrAnswerQuality
from evaluate.transfer_to_agent_quality import TransferToAgentQuality

# transfer_to_agent_quality
# evaluate(
#     experiment_name=TRANSFER_TO_AGENT_QUALITY + time.strftime("_%Y%m%d_%H%M%S"),
#     dataset=Opik().get_dataset(name=MATMASTER_SUBAGENT),
#     task=evaluation_task,
#     scoring_metrics=[TransferToAgentQuality(model="azure/gpt-4o")],
# )

# multi_options_quality
# evaluate(
#     experiment_name=MULTI_OPTION_QUALITY + time.strftime("_%Y%m%d_%H%M%S"),
#     dataset=Opik().get_dataset(name=MATMASTER_MULTI_OPTION),
#     task=evaluation_task,
#     scoring_metrics=[MultiOptionQuality(model="azure/gpt-4o")],
# )

# answer_quality
evaluate(
    experiment_name=MATMASTER_PLAN_QUALITY + time.strftime("_%Y%m%d_%H%M%S"),
    dataset=Opik().get_dataset(name=MATMASTER_PLAN_QUALITY),
    task=evaluation_task,
    scoring_metrics=[AnswerRelevance(name=MATMASTER_PLAN_QUALITY, model="azure/gpt-4o", require_context=False)],
)

# multi_turn_answer_quality
# evaluate(
#     experiment_name=MATMASTER_MULTI_TURN_ANSWER_QUALITY + time.strftime("_%Y%m%d_%H%M%S"),
#     dataset=Opik().get_dataset(name=MATMASTER_MULTI_TURN_ANSWER_QUALITY),
#     task=multi_turn_evaluation_task,
#     scoring_metrics=[
#         AnswerRelevance(name=MATMASTER_MULTI_TURN_ANSWER_QUALITY, model="azure/gpt-4o", require_context=False)],
# )

# transfer_and_answer_quality
# evaluate(
#     experiment_name=MATMASTER_TRANSFER_OR_ANSWER_QUALITY + time.strftime("_%Y%m%d_%H%M%S"),
#     dataset=Opik().get_dataset(name=MATMASTER_TRANSFER_OR_ANSWER_QUALITY),
#     task=evaluation_task,
#     scoring_metrics=[TransferOrAnswerQuality(model="azure/gpt-4o")],
# )
