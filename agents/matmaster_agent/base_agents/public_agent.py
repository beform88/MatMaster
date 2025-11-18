import copy
import logging
from typing import AsyncGenerator, Union, override

from google.adk.agents import InvocationContext, SequentialAgent
from google.adk.events import Event
from google.adk.models import BaseLlm
from pydantic import computed_field, model_validator

from agents.matmaster_agent.base_agents.disallow_transfer_agent import (
    DisallowTransferLlmAgent,
)
from agents.matmaster_agent.base_agents.error_agent import (
    ErrorHandleLlmAgent,
)
from agents.matmaster_agent.base_agents.mcp_agent import MCPInitMixin
from agents.matmaster_agent.base_agents.schema_agent import SchemaAgent
from agents.matmaster_agent.base_agents.subordinate_agent import (
    SubordinateFeaturesMixin,
)
from agents.matmaster_agent.base_agents.sync_agent import (
    SyncMCPAgent,
    ToolValidatorAgent,
)
from agents.matmaster_agent.base_callbacks.private_callback import (
    default_before_model_callback,
    remove_function_call,
)
from agents.matmaster_agent.constant import MATMASTER_AGENT_NAME
from agents.matmaster_agent.job_agents.recommend_params_agent.prompt import (
    gen_recommend_params_agent_instruction,
)
from agents.matmaster_agent.job_agents.recommend_params_agent.schema import (
    create_tool_args_schema,
)
from agents.matmaster_agent.job_agents.tool_call_info_agent.prompt import (
    gen_tool_call_info_instruction,
)
from agents.matmaster_agent.job_agents.tool_call_info_agent.utils import (
    update_tool_call_info_with_function_declarations,
    update_tool_call_info_with_recommend_params,
)
from agents.matmaster_agent.llm_config import MatMasterLlmConfig
from agents.matmaster_agent.logger import PrefixFilter
from agents.matmaster_agent.model import ToolCallInfoSchema
from agents.matmaster_agent.utils.event_utils import (
    update_state_event,
)

logger = logging.getLogger(__name__)
logger.addFilter(PrefixFilter(MATMASTER_AGENT_NAME))
logger.setLevel(logging.INFO)


# 同步计算 Agent，可自动 transfer 回主 Agent
class BaseSyncAgent(SubordinateFeaturesMixin, SyncMCPAgent):
    pass


class BaseSyncAgentWithToolValidator(
    SubordinateFeaturesMixin, MCPInitMixin, ErrorHandleLlmAgent
):
    model: Union[str, BaseLlm]
    instruction: str
    tools: list

    @model_validator(mode='after')
    def after_init(self):
        agent_prefix = self.name.replace('_agent', '')

        self._tool_call_info_agent = SchemaAgent(
            model=self.model,
            name=f"{agent_prefix}_tool_call_info_agent",
            tools=self.tools,
            disallow_transfer_to_parent=True,
            disallow_transfer_to_peers=True,
            before_model_callback=default_before_model_callback,
            after_model_callback=remove_function_call,
            output_schema=ToolCallInfoSchema,
            state_key='tool_call_info',
        )

        self._recommend_params_agent = DisallowTransferLlmAgent(
            model=self.model,
            name=f"{agent_prefix}_recommend_params_agent",
            instruction=gen_recommend_params_agent_instruction(),
            tools=self.tools,
            after_model_callback=remove_function_call,
        )

        self._recommend_params_schema_agent = SchemaAgent(
            model=MatMasterLlmConfig.tool_schema_model,
            name=f"{agent_prefix}_recommend_params_schema_agent",
            state_key='recommend_params',
        )

        sync_mcp_agent = SyncMCPAgent(
            model=self.model,
            name=f"{agent_prefix}_sync_mcp_agent",
            description=self.description,
            instruction=self.instruction,
            tools=self.tools,
            disallow_transfer_to_peers=True,
            disallow_transfer_to_parent=True,
            after_model_callback=self.after_model_callback,
            enable_tgz_unpack=self.enable_tgz_unpack,
            cost_func=self.cost_func,
            render_tool_response=self.render_tool_response,
        )

        tool_validator_agent = ToolValidatorAgent(
            name=f"{agent_prefix}_tool_validator_agent",
        )

        self._submit_agent = SequentialAgent(
            name=f"{agent_prefix}_submit_agent",
            sub_agents=[sync_mcp_agent, tool_validator_agent],
        )

        self.sub_agents = [
            self.tool_call_info_agent,
            self.recommend_params_agent,
            self.submit_agent,
        ]

        return self

    @computed_field
    @property
    def tool_call_info_agent(self) -> SchemaAgent:
        return self._tool_call_info_agent

    @computed_field
    @property
    def recommend_params_agent(self) -> DisallowTransferLlmAgent:
        return self._recommend_params_agent

    @computed_field
    @property
    def recommend_params_schema_agent(self) -> SchemaAgent:
        return self._recommend_params_schema_agent

    @computed_field
    @property
    def submit_agent(self) -> SequentialAgent:
        return self._submit_agent

    @override
    async def _run_events(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        # 根据计划来
        current_step = ctx.session.state['plan']['steps'][
            ctx.session.state['plan_index']
        ]
        self.tool_call_info_agent.instruction = gen_tool_call_info_instruction(
            user_prompt=current_step['description']
        )
        async for tool_call_info_event in self.tool_call_info_agent.run_async(ctx):
            yield tool_call_info_event

        if ctx.session.state['error_occurred']:
            return

        if not ctx.session.state['tool_call_info']:
            update_tool_call_info = copy.deepcopy(ctx.session.state['tool_call_info'])
            update_tool_call_info['tool_name'] = current_step['tool_name']
            update_tool_call_info['tool_args'] = {}
            update_tool_call_info['missing_tool_args'] = []
            yield update_state_event(
                ctx, state_delta={'tool_call_info': update_tool_call_info}
            )

        if ctx.session.state['tool_call_info']['tool_name'].startswith('functions.'):
            logger.warning(
                f'{ctx.session.id} Detect wrong tool_name: {ctx.session.state['tool_call_info']['tool_name']}'
            )
            update_tool_call_info = copy.deepcopy(ctx.session.state['tool_call_info'])
            update_tool_call_info['tool_name'] = update_tool_call_info[
                'tool_name'
            ].replace('functions.', '')
            yield update_state_event(
                ctx, state_delta={'tool_call_info': update_tool_call_info}
            )

        tool_call_info = ctx.session.state['tool_call_info']
        function_declarations = ctx.session.state['function_declarations']
        tool_call_info, current_function_declaration = (
            update_tool_call_info_with_function_declarations(
                tool_call_info, function_declarations
            )
        )

        yield update_state_event(ctx, state_delta={'tool_call_info': tool_call_info})

        logger.info(
            f'{ctx.session.id} tool_call_info_with_function_declarations = {tool_call_info}'
        )

        missing_tool_args = tool_call_info.get('missing_tool_args', None)
        if missing_tool_args:
            async for recommend_params_event in self.recommend_params_agent.run_async(
                ctx
            ):
                yield recommend_params_event

            self.recommend_params_schema_agent.output_schema = create_tool_args_schema(
                missing_tool_args, current_function_declaration
            )
            async for (
                recommend_params_schema_event
            ) in self.recommend_params_schema_agent.run_async(ctx):
                yield recommend_params_schema_event

            recommend_params = ctx.session.state['recommend_params']
            tool_call_info = update_tool_call_info_with_recommend_params(
                tool_call_info, recommend_params
            )
            yield update_state_event(
                ctx, state_delta={'tool_call_info': tool_call_info}
            )
            logger.info(
                f'{ctx.session.id} tool_call_info_with_recommend_params = {ctx.session.state['tool_call_info']}'
            )

        # 前置 tool_hallucination 为 False
        yield update_state_event(ctx, state_delta={'tool_hallucination': False})
        for _ in range(2):
            async for submit_event in self.submit_agent.run_async(ctx):
                yield submit_event

            if not ctx.session.state['tool_hallucination']:
                break
