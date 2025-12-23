import json
import logging
from typing import Optional

from google.adk.agents import InvocationContext

from agents.matmaster_agent.base_agents.schema_agent import SchemaAgent
from agents.matmaster_agent.constant import ModelRole
from agents.matmaster_agent.flow_agents.plan_make_agent.agent import PlanMakeAgent
from agents.matmaster_agent.flow_agents.plan_make_agent.utils import normalize_plan_state
from agents.matmaster_agent.flow_agents.plan_make_agent.prompt import (
    get_plan_make_instruction,
)
from agents.matmaster_agent.flow_agents.tot.prompt import (
    branching_instruction,
    refinement_instruction,
    scoring_instruction,
)
from agents.matmaster_agent.flow_agents.tot.schema import ThoughtEvaluationSchema
from agents.matmaster_agent.flow_agents.utils import create_dynamic_plan_schema
from agents.matmaster_agent.llm_config import MatMasterLlmConfig
from agents.matmaster_agent.prompt import GLOBAL_INSTRUCTION
from agents.matmaster_agent.utils.event_utils import is_function_call

logger = logging.getLogger(__name__)


class TreeOfThoughtPlanner:
    def __init__(
        self,
        model_config: MatMasterLlmConfig,
        branch_factor: int = 3,
        beam_width: int = 2,
        max_depth: int = 2,
    ) -> None:
        self.branch_factor = branch_factor
        self.beam_width = beam_width
        self.max_depth = max_depth

        self._plan_generator = PlanMakeAgent(
            name='tot_plan_make_agent',
            model=model_config.tool_schema_model,
            description='Generate plan candidates for Tree-of-Thoughts search',
            disallow_transfer_to_parent=True,
            disallow_transfer_to_peers=True,
            state_key=None,
        )

        self._score_agent = SchemaAgent(
            name='tot_plan_score_agent',
            model=model_config.tool_schema_model,
            description='Score Tree-of-Thoughts branches',
            instruction='',
            disallow_transfer_to_parent=True,
            disallow_transfer_to_peers=True,
            output_schema=ThoughtEvaluationSchema,
            state_key=None,
            global_instruction=GLOBAL_INSTRUCTION,
            role=ModelRole,
        )

    async def search_best_plan(
        self,
        ctx: InvocationContext,
        available_tools_with_info_str: str,
        available_tools: list[str],
        plan_prompt_suffix: str = '',
    ) -> Optional[dict]:
        """Perform a lightweight Tree-of-Thoughts search to pick the best plan."""

        plan_instruction = get_plan_make_instruction(
            available_tools_with_info_str + plan_prompt_suffix
        )
        output_schema = create_dynamic_plan_schema(available_tools)

        initial_candidates = await self._generate_candidates(
            ctx, plan_instruction, output_schema, available_tools_with_info_str
        )
        if not initial_candidates:
            return None

        frontier = self._select_top(initial_candidates)

        for depth in range(2, self.max_depth + 1):
            refined_candidates = []
            for plan, evaluation in frontier:
                feedback = '\n'.join(evaluation.reasons + evaluation.risks)
                refine_instruction = plan_instruction + refinement_instruction(
                    json.dumps(plan, ensure_ascii=False), feedback
                )
                refined_plan = await self._generate_single_plan(
                    ctx,
                    refine_instruction,
                    output_schema,
                    branch_label=f'refine_{depth}',
                )
                if not refined_plan:
                    continue

                refined_score = await self._score_plan(
                    ctx, refined_plan, available_tools_with_info_str
                )
                if refined_score and refined_score.keep:
                    refined_candidates.append((refined_plan, refined_score))

            if refined_candidates:
                frontier = self._select_top(refined_candidates)
            else:
                break

        best_plan, _ = max(frontier, key=lambda item: item[1].score)
        return normalize_plan_state(best_plan)

    async def _generate_candidates(
        self,
            ctx: InvocationContext,
            plan_instruction: str,
            output_schema,
            tools_info: str,
    ) -> list[tuple[dict, ThoughtEvaluationSchema]]:
        scored_plans = []
        for idx in range(self.branch_factor):
            plan = await self._generate_single_plan(
                ctx,
                plan_instruction + branching_instruction(idx + 1, self.max_depth),
                output_schema,
                branch_label=f'branch_{idx + 1}',
            )
            if not plan:
                continue
            evaluation = await self._score_plan(
                ctx, plan, tools_info
            )
            if evaluation and evaluation.keep:
                scored_plans.append((plan, evaluation))

        return scored_plans

    async def _generate_single_plan(
        self,
        ctx: InvocationContext,
        instruction: str,
        output_schema,
        branch_label: str,
    ) -> Optional[dict]:
        plan_schema = None
        self._plan_generator.instruction = instruction
        self._plan_generator.output_schema = output_schema

        async for event in self._plan_generator.run_async(ctx):
            if is_function_call(event):
                try:
                    for part in event.content.parts:
                        if part.function_call and part.function_call.args:
                            plan_schema = part.function_call.args
                            break
                except Exception as err:  # pragma: no cover - defensive
                    logger.warning(
                        f'{ctx.session.id} failed to parse plan for {branch_label}: {err}'
                    )

        if not plan_schema:
            logger.warning(f'{ctx.session.id} no plan generated for {branch_label}')
        return plan_schema

    async def _score_plan(
        self, ctx: InvocationContext, plan: dict, tools_info: str
    ) -> Optional[ThoughtEvaluationSchema]:
        score_instruction = scoring_instruction(
            ctx.user_content.parts[0].text, tools_info
        )
        self._score_agent.instruction = score_instruction

        evaluation = None
        async for event in self._score_agent.run_async(ctx):
            if is_function_call(event):
                for part in event.content.parts:
                    if part.function_call and part.function_call.args:
                        evaluation = ThoughtEvaluationSchema(**part.function_call.args)
                        break

        if not evaluation:
            logger.warning(f'{ctx.session.id} scoring failed for plan')
        return evaluation

    def _select_top(
        self, candidates: list[tuple[dict, ThoughtEvaluationSchema]]
    ) -> list[tuple[dict, ThoughtEvaluationSchema]]:
        return sorted(
            candidates, key=lambda item: item[1].score, reverse=True
        )[: self.beam_width]
