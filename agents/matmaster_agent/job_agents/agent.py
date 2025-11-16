import logging
from typing import AsyncGenerator, Optional, Union, override

from google.adk.agents import InvocationContext, SequentialAgent
from google.adk.events import Event
from google.adk.models import BaseLlm
from pydantic import Field, computed_field, model_validator

from agents.matmaster_agent.base_agents.disallow_transfer_agent import (
    DisallowTransferLlmAgent,
)
from agents.matmaster_agent.base_agents.error_agent import ErrorHandleBaseAgent
from agents.matmaster_agent.base_agents.mcp_agent import MCPInitMixin
from agents.matmaster_agent.base_agents.schema_agent import SchemaAgent
from agents.matmaster_agent.base_agents.subordinate_agent import (
    SubordinateFeaturesMixin,
)
from agents.matmaster_agent.base_callbacks.private_callback import (
    default_before_model_callback,
    remove_function_call,
)
from agents.matmaster_agent.constant import (
    FRONTEND_STATE_KEY,
    MATMASTER_AGENT_NAME,
    ModelRole,
)
from agents.matmaster_agent.flow_agents.scene_agent.model import SceneEnum
from agents.matmaster_agent.job_agents.recommend_params_agent.prompt import (
    gen_recommend_params_agent_instruction,
)
from agents.matmaster_agent.job_agents.recommend_params_agent.schema import (
    create_tool_args_schema,
)
from agents.matmaster_agent.job_agents.result_core_agent.agent import (
    ResultMCPAgent,
)
from agents.matmaster_agent.job_agents.submit_core_agent.agent import (
    SubmitCoreMCPAgent,
)
from agents.matmaster_agent.job_agents.submit_core_agent.prompt import (
    gen_submit_core_agent_instruction,
)
from agents.matmaster_agent.job_agents.submit_render_agent.agent import (
    SubmitRenderAgent,
)
from agents.matmaster_agent.job_agents.submit_validator_agent.agent import (
    SubmitValidatorAgent,
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
    context_function_event,
    update_state_event,
)
from agents.matmaster_agent.utils.helper_func import get_session_state

logger = logging.getLogger(__name__)
logger.addFilter(PrefixFilter(MATMASTER_AGENT_NAME))
logger.setLevel(logging.INFO)


class BaseAsyncJobAgent(SubordinateFeaturesMixin, MCPInitMixin, ErrorHandleBaseAgent):
    """
    Base agent class for handling asynchronous job submissions.

    Agents that need to submit asynchronous tasks should inherit from this class.
    It provides a complete workflow for job submission, result retrieval, and
    parameter validation through specialized sub-agents.
    """

    model: Union[str, BaseLlm] = MatMasterLlmConfig.default_litellm_model
    agent_instruction: str
    mcp_tools: list
    dflow_flag: bool = Field(
        False,
        description='Indicates if this agent is related to dflow workflows',
        exclude=True,
    )
    sync_tools: Optional[list] = Field(
        None,
        description='List of tools that will be executed synchronously on the server',
    )

    @model_validator(mode='after')
    def after_init(self):
        agent_prefix = self.name.replace('_agent', '')

        # Create submission workflow agents
        submit_core_agent = SubmitCoreMCPAgent(
            model=self.model,
            name=f"{agent_prefix}_submit_core_agent",
            description=f"A specialized {agent_prefix} job submit agent",
            instruction=gen_submit_core_agent_instruction(agent_prefix),
            tools=self.mcp_tools,
            disallow_transfer_to_parent=True,
            enable_tgz_unpack=self.enable_tgz_unpack,
            cost_func=self.cost_func,
        )

        submit_render_agent = SubmitRenderAgent(
            model=self.model, name=f"{agent_prefix}_submit_render_agent"
        )

        submit_validator_agent = SubmitValidatorAgent(
            name=f"{agent_prefix}_submit_validator_agent"
        )

        # Create sequential agent for submission process
        self._submit_agent = SequentialAgent(
            name=f"{agent_prefix}_submit_agent",
            description=f"Coordinates {agent_prefix} job submission and frontend task queue display",
            sub_agents=[submit_core_agent, submit_render_agent, submit_validator_agent],
        )

        # Create result retrieval agent
        result_core_agent = ResultMCPAgent(
            model=self.model,
            name=f"{agent_prefix}_result_core_agent",
            tools=self.mcp_tools,
            enable_tgz_unpack=self.enable_tgz_unpack,
        )

        self._result_agent = SequentialAgent(
            name=f"{agent_prefix}_result_agent",
            description='Query status and retrieve results',
            sub_agents=[result_core_agent],
        )

        self._recommend_params_agent = DisallowTransferLlmAgent(
            model=self.model,
            name=f"{agent_prefix}_recommend_params_agent",
            instruction=gen_recommend_params_agent_instruction(),
            tools=self.mcp_tools,
            after_model_callback=remove_function_call,
        )

        self._recommend_params_schema_agent = SchemaAgent(
            model=MatMasterLlmConfig.tool_schema_model,
            name=f"{agent_prefix}_recommend_params_schema_agent",
            state_key='recommend_params',
        )

        self._tool_call_info_agent = SchemaAgent(
            model=self.model,
            name=f"{agent_prefix}_tool_call_info_agent",
            tools=self.mcp_tools,
            disallow_transfer_to_parent=True,
            disallow_transfer_to_peers=True,
            before_model_callback=default_before_model_callback,
            after_model_callback=remove_function_call,
            output_schema=ToolCallInfoSchema,
            state_key='tool_call_info',
        )

        self.sub_agents = [
            self.submit_agent,
            self.result_agent,
            self.recommend_params_agent,
            self.tool_call_info_agent,
        ]

        return self

    @computed_field
    @property
    def submit_agent(self) -> SequentialAgent:
        return self._submit_agent

    @computed_field
    @property
    def result_agent(self) -> SequentialAgent:
        return self._result_agent

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
    def tool_call_info_agent(self) -> SchemaAgent:
        return self._tool_call_info_agent

    @override
    async def _run_events(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        yield update_state_event(
            ctx,
            state_delta={
                'dflow': self.dflow_flag,
                'sync_tools': self.sync_tools,
            },
        )

        async for result_event in self.result_agent.run_async(ctx):
            yield result_event

        session_state = get_session_state(ctx)
        frontend_origin_id = session_state[FRONTEND_STATE_KEY]['biz'].get('origin_id')
        # 检查是否需要查询任务结果
        has_origin_job_id = session_state.get('origin_job_id') is not None
        has_matching_job = (
            frontend_origin_id is not None
            and frontend_origin_id in session_state.get('long_running_jobs', {})
            and ctx.invocation_id
            == session_state['long_running_jobs'][frontend_origin_id][
                'last_invocation_id'
            ]
        )
        logger.info(
            f'{ctx.session.id} has_origin_job_id = {has_origin_job_id}, has_matching_job = {has_matching_job}, {ctx.invocation_id}, {session_state['long_running_jobs']}'
        )

        if (
            has_origin_job_id
            or has_matching_job
            or ctx.session.state['scene']['type'][0] == SceneEnum.JobResultRetrieval
        ):
            # Only Query Job Result
            pass
        else:
            # 根据计划来
            current_step = session_state['plan']['steps'][session_state['plan_index']]
            for materials_plan_function_call_event in context_function_event(
                ctx,
                self.name,
                'materials_plan_function_call',
                {
                    'msg': f'According to the plan, I will call the `{current_step['tool_name']}`: {current_step['description']}'
                },
                ModelRole,
            ):
                yield materials_plan_function_call_event

            self.tool_call_info_agent.instruction = gen_tool_call_info_instruction(
                user_prompt=current_step['description']
            )
            async for tool_call_info_event in self.tool_call_info_agent.run_async(ctx):
                yield tool_call_info_event
            tool_call_info = ctx.session.state['tool_call_info']
            function_declarations = ctx.session.state['function_declarations']
            tool_call_info, current_function_declaration = (
                update_tool_call_info_with_function_declarations(
                    tool_call_info, function_declarations
                )
            )

            yield update_state_event(
                ctx, state_delta={'tool_call_info': tool_call_info}
            )

            logger.info(
                f'{ctx.session.id} tool_call_info_with_function_declarations = {tool_call_info}'
            )

            missing_tool_args = tool_call_info.get('missing_tool_args', None)
            if missing_tool_args:
                async for (
                    recommend_params_event
                ) in self.recommend_params_agent.run_async(ctx):
                    yield recommend_params_event

                self.recommend_params_schema_agent.output_schema = (
                    create_tool_args_schema(
                        missing_tool_args, current_function_declaration
                    )
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
            yield update_state_event(ctx, state_delta={'validation_error': False})
            for _ in range(2):
                async for submit_event in self.submit_agent.run_async(ctx):
                    yield submit_event

                if not ctx.session.state['tool_hallucination']:
                    break
