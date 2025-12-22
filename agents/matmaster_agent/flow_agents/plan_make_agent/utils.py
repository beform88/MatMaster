import copy

from agents.matmaster_agent.flow_agents.model import PlanStepStatusEnum


def normalize_plan_state(plan: dict) -> dict:
    """Standardize plan structure and compute feasibility flags.

    The helper mirrors the post-processing done by :class:`PlanMakeAgent` so
    that callers that build or refine plans outside the agent can align with
    the expected session state structure.
    """

    update_plan = copy.deepcopy(plan) if plan else {'steps': []}
    update_plan.setdefault('steps', [])
    update_plan['feasibility'] = 'null'

    normalized_steps = []
    for step in update_plan['steps']:
        step_copy = copy.deepcopy(step)
        step_copy.setdefault('status', PlanStepStatusEnum.PLAN.value)
        if not step_copy.get('tool_name'):
            step_copy['tool_name'] = 'llm_tool'
        normalized_steps.append(step_copy)

    update_plan['steps'] = normalized_steps

    total_steps = len(update_plan['steps'])
    exist_step = 0
    for index, step in enumerate(update_plan['steps']):
        if index == 0 and not step['tool_name']:
            break
        if step['tool_name']:
            exist_step += 1
        else:
            break

    if not exist_step:
        pass
    elif exist_step != total_steps:
        update_plan['feasibility'] = 'part'
    else:
        update_plan['feasibility'] = 'full'

    return update_plan
