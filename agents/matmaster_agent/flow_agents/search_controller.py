import copy
import logging
from typing import Callable, Iterable, List, Optional

from google.adk.agents import InvocationContext
from pydantic import create_model

from agents.matmaster_agent.flow_agents.plan_make_agent.agent import (
    PlanMakeAgent,
)
from agents.matmaster_agent.flow_agents.plan_make_agent.prompt import (
    get_multi_plan_make_instruction,
)
from agents.matmaster_agent.flow_agents.thought_node import ThoughtNode
from agents.matmaster_agent.flow_agents.utils import (
    create_dynamic_plan_schema,
    get_tools_list,
)
from agents.matmaster_agent.sub_agents.mapping import ALL_AGENT_TOOLS_LIST
from agents.matmaster_agent.sub_agents.tools import ALL_TOOLS

logger = logging.getLogger(__name__)


class SearchController:
    def __init__(
        self,
        ctx: InvocationContext,
        plan_make_agent: PlanMakeAgent,
        *,
        width_limit: int = 4,
        depth_limit: int = 4,
        temperature: float = 0.7,
        candidate_count: int = 3,
        scorer: Optional[Callable[[ThoughtNode], float]] = None,
    ):
        self.ctx = ctx
        self.plan_make_agent = plan_make_agent
        self.width_limit = width_limit
        self.depth_limit = depth_limit
        self.temperature = temperature
        self.candidate_count = candidate_count
        self.scorer = scorer or (lambda node: float(len(node.actions)))

    def is_terminal(self, node: ThoughtNode) -> bool:
        if node.status == 'terminal':
            return True
        if node.depth >= self.depth_limit:
            return True
        return False

    async def expand(self, node: ThoughtNode) -> List[ThoughtNode]:
        if self.is_terminal(node):
            return []

        candidate_plans = await self._generate_candidates(node)
        expanded_nodes: List[ThoughtNode] = []
        for plan in candidate_plans[: self.width_limit]:
            child_state = copy.deepcopy(node.state_snapshot)
            child_state['plan'] = plan
            combined_actions = node.actions + plan.get('steps', [])
            expanded_nodes.append(
                ThoughtNode(
                    state_snapshot=child_state,
                    actions=combined_actions,
                    depth=node.depth + 1,
                    parent_id=node.id,
                )
            )

        return expanded_nodes

    def evaluate(self, nodes: Iterable[ThoughtNode]) -> List[ThoughtNode]:
        evaluated_nodes: List[ThoughtNode] = []
        for node in nodes:
            node.score = self.scorer(node)
            evaluated_nodes.append(node)
        return evaluated_nodes

    def select(self, nodes: Iterable[ThoughtNode]) -> List[ThoughtNode]:
        sorted_nodes = sorted(nodes, key=lambda node: node.score, reverse=True)
        selected = sorted_nodes[: self.width_limit]
        for node in sorted_nodes[self.width_limit :]:
            node.status = 'pruned'
        return selected

    async def _generate_candidates(self, node: ThoughtNode) -> List[dict]:
        available_tools, tool_info_prompt = self._build_available_tool_prompt(
            node
        )
        candidate_prompt = get_multi_plan_make_instruction(
            tool_info_prompt, self.candidate_count
        )
        candidate_schema = self._build_candidate_schema(available_tools)

        original_instruction = self.plan_make_agent.instruction
        original_schema = self.plan_make_agent.output_schema
        original_state_key = getattr(self.plan_make_agent, 'state_key', None)
        original_temperature = getattr(self.plan_make_agent.model, 'temperature', None)
        backup_state = copy.deepcopy(self.ctx.session.state)

        self.plan_make_agent.instruction = candidate_prompt
        self.plan_make_agent.output_schema = candidate_schema
        self.plan_make_agent.state_key = 'candidate_plans'
        if hasattr(self.plan_make_agent.model, 'temperature'):
            self.plan_make_agent.model.temperature = self.temperature

        try:
            self.ctx.session.state = copy.deepcopy(node.state_snapshot)
            async for _ in self.plan_make_agent.run_async(self.ctx):
                pass
            result = self.ctx.session.state.get('candidate_plans', {})
            return result.get('candidates', []) if isinstance(result, dict) else []
        finally:
            self.ctx.session.state = backup_state
            self.plan_make_agent.instruction = original_instruction
            self.plan_make_agent.output_schema = original_schema
            self.plan_make_agent.state_key = original_state_key
            if (
                hasattr(self.plan_make_agent.model, 'temperature')
                and original_temperature is not None
            ):
                self.plan_make_agent.model.temperature = original_temperature

    def _build_available_tool_prompt(self, node: ThoughtNode):
        scenes = node.state_snapshot.get('scenes', [])
        available_tools = get_tools_list(scenes) or ALL_AGENT_TOOLS_LIST
        available_tools_with_info = {
            item: {
                'scene': ALL_TOOLS[item]['scene'],
                'description': ALL_TOOLS[item]['description'],
            }
            for item in available_tools
            if item in ALL_TOOLS
        }
        available_tools_with_info_str = '\n'.join(
            [
                f"{key}\n    scene: {', '.join(value['scene'])}\n    description: {value['description']}"
                for key, value in available_tools_with_info.items()
            ]
        )
        return available_tools, available_tools_with_info_str

    def _build_candidate_schema(self, available_tools: list):
        dynamic_plan_schema = create_dynamic_plan_schema(available_tools)
        return create_model(
            'CandidatePlanListSchema',
            candidates=(List[dynamic_plan_schema], ...),
        )


__all__ = ['SearchController']
