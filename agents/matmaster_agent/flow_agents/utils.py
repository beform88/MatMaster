import logging
from typing import List, Literal, Optional

from google.adk.agents import InvocationContext
from pydantic import BaseModel, create_model

from agents.matmaster_agent.flow_agents.model import PlanStepStatusEnum
from agents.matmaster_agent.flow_agents.schema import FlowStatusEnum
from agents.matmaster_agent.sub_agents.mapping import ALL_AGENT_TOOLS_LIST
from agents.matmaster_agent.sub_agents.tools import ALL_TOOLS

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def get_tools_list(scenes: list):
    if not scenes:
        return ALL_AGENT_TOOLS_LIST
    else:
        return [
            k
            for k, v in ALL_TOOLS.items()
            if any(scene in v['scene'] for scene in scenes)
        ]


def get_agent_name(tool_name, sub_agents):
    try:
        target_agent_name = ALL_TOOLS[tool_name]['belonging_agent']
    except BaseException:
        raise RuntimeError(f"ToolName Error: {tool_name}")

    for sub_agent in sub_agents:
        if sub_agent.name == target_agent_name:
            return sub_agent


def check_plan(ctx: InvocationContext):
    if not ctx.session.state.get('plan'):
        return FlowStatusEnum.NO_PLAN

    if ctx.session.state['plan']['feasibility'] == 'null':
        return FlowStatusEnum.NO_PLAN

    plan_json = ctx.session.state['plan']
    plan_step_count = 0  # 统计状态为 plan 的 step 个数
    process_step_count = 0
    failed_step_count = 0
    total_steps = len(plan_json['steps'])
    for step in plan_json['steps']:
        if step['status'] == PlanStepStatusEnum.PLAN:
            plan_step_count += 1
        elif step['status'] in [
            PlanStepStatusEnum.PROCESS,
            PlanStepStatusEnum.SUBMITTED,
        ]:
            process_step_count += 1
        elif step['status'] == PlanStepStatusEnum.FAILED:
            failed_step_count += 1

    if (not plan_step_count and not process_step_count) or failed_step_count:
        return FlowStatusEnum.COMPLETE
    elif plan_step_count == total_steps:
        return FlowStatusEnum.NEW_PLAN
    else:
        return FlowStatusEnum.PROCESS


def create_dynamic_plan_schema(available_tools: list):
    # 动态创建 PlanStepSchema
    DynamicPlanStepSchema = create_model(
        'DynamicPlanStepSchema',
        tool_name=(Optional[Literal[tuple(available_tools)]], None),
        description=(str, ...),
        status=(
            Literal[tuple(PlanStepStatusEnum.__members__.values())],
            PlanStepStatusEnum.PLAN.value,
        ),
        __base__=BaseModel,
    )

    # 动态创建 PlanSchema
    DynamicPlanSchema = create_model(
        'DynamicPlanSchema',
        steps=(List[DynamicPlanStepSchema], ...),
        __base__=BaseModel,
    )

    return DynamicPlanSchema


def should_bypass_confirmation(ctx: InvocationContext) -> bool:
    """
    Determine whether to skip plan confirmation based on the tools in the plan.

    Returns True if the plan contains exactly one step with a tool that is in
    the BYPASS_CONFIRMATION_TOOLS list.
    """
    BYPASS_CONFIRMATION_TOOLS = [
        'web-search',
        'extract_info_from_webpage',
        'search-papers-normal',
        'search-papers-enhanced',
    ]

    plan_steps = ctx.session.state['plan'].get('steps', [])
    tool_count = len(
        plan_steps
    )  # plan steps are `actual_steps` validated by `tool_name` before appended

    # Check if there is exactly one tool in the plan
    if tool_count == 1:
        # Find the first (and only) tool name
        first_tool_name = plan_steps[0].get('tool_name', '')

        # Check if this tool is in the bypass list
        if first_tool_name in BYPASS_CONFIRMATION_TOOLS:
            return True

    return False
