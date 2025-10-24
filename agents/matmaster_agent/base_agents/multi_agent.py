import json
import logging
from typing import AsyncGenerator, Optional, override

import litellm
from google.adk.agents import InvocationContext, LlmAgent, SequentialAgent
from google.adk.events import Event
from pydantic import Field

from agents.matmaster_agent.base_agents.error_agent import ErrorHandleAgent
from agents.matmaster_agent.base_agents.job_agent import (
    ParamsCheckInfoAgent,
    ResultCalculationMCPLlmAgent,
    SubmitCoreCalculationMCPLlmAgent,
    SubmitRenderAgent,
    SubmitValidatorAgent,
    ToolCallInfoAgent,
)
from agents.matmaster_agent.base_agents.mcp_agent import (
    MCPFeaturesMixin,
    NonSubMCPLlmAgent,
)
from agents.matmaster_agent.base_agents.sflow_agent import (
    ToolValidatorAgent,
)
from agents.matmaster_agent.base_agents.subordinate_agent import (
    SubordinateFeaturesMixin,
)
from agents.matmaster_agent.base_callbacks.private_callback import remove_function_call
from agents.matmaster_agent.constant import (
    FRONTEND_STATE_KEY,
    MATMASTER_AGENT_NAME,
    ModelRole,
)
from agents.matmaster_agent.model import CostFuncType, ParamsCheckComplete
from agents.matmaster_agent.prompt import (
    gen_params_check_completed_agent_instruction,
    gen_params_check_info_agent_instruction,
    gen_result_agent_description,
    gen_result_core_agent_instruction,
    gen_submit_agent_description,
    gen_submit_core_agent_description,
    gen_submit_core_agent_instruction,
    gen_tool_call_info_instruction,
)
from agents.matmaster_agent.utils.event_utils import (
    cherry_pick_events,
    context_function_event,
    update_state_event,
)
from agents.matmaster_agent.utils.helper_func import (
    get_session_state,
)

logger = logging.getLogger(__name__)


class BaseSyncSubAgent(MCPFeaturesMixin, SubordinateFeaturesMixin, ErrorHandleAgent):
    def __init__(self, *args, supervisor_agent=None, **kwargs):
        # 确保 supervisor_agent 被正确处理
        super().__init__(*args, supervisor_agent=supervisor_agent, **kwargs)


class BaseSyncSubAgentWithToolValidator(SubordinateFeaturesMixin, ErrorHandleAgent):
    sync_mcp_agent: NonSubMCPLlmAgent
    tool_validator_agent: ToolValidatorAgent
    enable_tgz_unpack: bool = Field(
        True, description='Whether to automatically unpack tgz files from tool results'
    )
    render_tool_response: bool = Field(
        False, description='Whether render tool response in frontend', exclude=True
    )
    cost_func: Optional[CostFuncType] = None

    def __init__(
        self,
        model,
        name: str,
        description: str,
        instruction: str,
        tools: list,
        supervisor_agent: str,
        enable_tgz_unpack: bool = True,
        cost_func: Optional[CostFuncType] = None,
        render_tool_response=False,
    ):
        agent_prefix = name.replace('_agent', '')

        sync_mcp_agent = NonSubMCPLlmAgent(
            model=model,
            name=f"{agent_prefix}_sync_mcp_agent",
            description=description,
            instruction=instruction,
            tools=tools,
            disallow_transfer_to_peers=True,
            disallow_transfer_to_parent=True,
            enable_tgz_unpack=enable_tgz_unpack,
            cost_func=cost_func,
            render_tool_response=render_tool_response,
        )

        tool_validator_agent = ToolValidatorAgent(
            model=model,
            name=f"{agent_prefix}_tool_validator_agent",
            disallow_transfer_to_peers=True,
            disallow_transfer_to_parent=True,
        )

        # Initialize parent class
        super().__init__(
            name=name,
            model=model,
            description=description,
            instruction=instruction,
            sync_mcp_agent=sync_mcp_agent,
            tool_validator_agent=tool_validator_agent,
            sub_agents=[
                sync_mcp_agent,
                tool_validator_agent,
            ],
            supervisor_agent=supervisor_agent,
            enable_tgz_unpack=enable_tgz_unpack,
            cost_func=cost_func,
        )

    @override
    async def _run_events(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        yield update_state_event(ctx, state_delta={'tool_hallucination': False})
        for _ in range(2):
            async for sync_mcp_event in self.sync_mcp_agent.run_async(ctx):
                yield sync_mcp_event

            async for tool_validator_event in self.tool_validator_agent.run_async(ctx):
                yield tool_validator_event

            if not ctx.session.state['tool_hallucination']:
                break


class BaseAsyncJobAgent(SubordinateFeaturesMixin, ErrorHandleAgent):
    """
    Base agent class for handling asynchronous job submissions.

    Agents that need to submit asynchronous tasks should inherit from this class.
    It provides a complete workflow for job submission, result retrieval, and
    parameter validation through specialized sub-agents.
    """

    submit_agent: SequentialAgent
    result_agent: SequentialAgent
    params_check_info_agent: LlmAgent
    tool_call_info_agent: LlmAgent
    dflow_flag: bool = Field(
        False,
        description='Indicates if this agent is related to dflow workflows',
        exclude=True,
    )
    supervisor_agent: str
    sync_tools: Optional[list] = Field(
        None,
        description='List of tools that will be executed synchronously on the server',
    )
    enable_tgz_unpack: bool = Field(
        True, description='Whether to automatically unpack tgz files from tool results'
    )
    cost_func: Optional[CostFuncType] = None

    def __init__(
        self,
        model,
        agent_name: str,
        agent_description: str,
        agent_instruction: str,
        *args,
        mcp_tools: list,
        dflow_flag: bool,
        supervisor_agent: str,
        sync_tools: Optional[list] = None,
        enable_tgz_unpack: bool = True,
        cost_func=None,
        **kwargs,
    ):
        """
        Initialize the BaseAsyncJobAgent with specialized sub-agents.

        Args:
            model: The language model to use
            agent_name: Name identifier for the agent
            agent_description: Description of the agent's purpose
            agent_instruction: Instructions for the agent's behavior
            mcp_tools: List of MCP tools available to the agent
            dflow_flag: Whether this agent is related to dflow workflows
            supervisor_agent: Identifier for the supervisor agent
            sync_tools: Tools to run synchronously on the server
            enable_tgz_unpack: Whether to unpack tgz files from results
            cost_func: Optional cost calculation function
        """
        agent_prefix = agent_name.replace('_agent', '')

        # Create submission workflow agents
        submit_core_agent = SubmitCoreCalculationMCPLlmAgent(
            model=model,
            name=f"{agent_prefix}_submit_core_agent",
            description=gen_submit_core_agent_description(agent_prefix),
            instruction=gen_submit_core_agent_instruction(agent_prefix),
            tools=mcp_tools,
            disallow_transfer_to_parent=True,
            enable_tgz_unpack=enable_tgz_unpack,
            cost_func=cost_func,
        )

        submit_render_agent = SubmitRenderAgent(
            model=model, name=f"{agent_prefix}_submit_render_agent"
        )

        submit_validator_agent = SubmitValidatorAgent(
            model=model, name=f"{agent_prefix}_submit_validator_agent"
        )

        # Create sequential agent for submission process
        submit_agent = SequentialAgent(
            name=f"{agent_prefix}_submit_agent",
            description=gen_submit_agent_description(agent_prefix),
            sub_agents=[submit_core_agent, submit_render_agent, submit_validator_agent],
        )

        # Create result retrieval agent
        result_core_agent = ResultCalculationMCPLlmAgent(
            model=model,
            name=f"{agent_prefix}_result_core_agent",
            tools=mcp_tools,
            instruction=gen_result_core_agent_instruction(agent_prefix),
            enable_tgz_unpack=enable_tgz_unpack,
        )

        result_agent = SequentialAgent(
            name=f"{agent_prefix}_result_agent",
            description=gen_result_agent_description(),
            sub_agents=[result_core_agent],
        )

        # Create validation and information agents
        params_check_info_agent = ParamsCheckInfoAgent(
            model=model,
            name=f"{agent_prefix}_params_check_info_agent",
            instruction=gen_params_check_info_agent_instruction(),
            tools=mcp_tools,
            disallow_transfer_to_parent=True,
            disallow_transfer_to_peers=True,
            after_model_callback=remove_function_call,
        )

        tool_call_info_agent = ToolCallInfoAgent(
            model=model,
            name=f"{agent_prefix}_tool_call_info_agent",
            instruction=gen_tool_call_info_instruction(),
            tools=mcp_tools,
            disallow_transfer_to_parent=True,
            disallow_transfer_to_peers=True,
            after_model_callback=remove_function_call,
        )

        # Initialize parent class
        super().__init__(
            name=agent_name,
            model=model,
            description=agent_description,
            submit_agent=submit_agent,
            result_agent=result_agent,
            params_check_info_agent=params_check_info_agent,
            tool_call_info_agent=tool_call_info_agent,
            dflow_flag=dflow_flag,
            sub_agents=[
                submit_agent,
                result_agent,
                params_check_info_agent,
                tool_call_info_agent,
            ],
            supervisor_agent=supervisor_agent,
            sync_tools=sync_tools,
            enable_tgz_unpack=enable_tgz_unpack,
            cost_func=cost_func,
        )

        self.cost_func = cost_func

    @override
    async def _run_events(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        session_state = get_session_state(ctx)
        yield update_state_event(
            ctx, state_delta={'dflow': self.dflow_flag, 'sync_tools': self.sync_tools}
        )

        async for result_event in self.result_agent.run_async(ctx):
            yield result_event

        if session_state.get('origin_job_id', None) is not None or (
            session_state[FRONTEND_STATE_KEY]['biz'].get('origin_id', None) is not None
            and list(session_state['long_running_jobs'].keys())
            and session_state[FRONTEND_STATE_KEY]['biz']['origin_id']
            in list(session_state['long_running_jobs'].keys())
        ):  # Only Query Job Result
            pass
        else:
            cherry_pick_parts = cherry_pick_events(ctx)[-5:]
            context_messages = '\n'.join(
                [
                    f'<{item[0].title()}> said: \n{item[1]}\n'
                    for item in cherry_pick_parts
                ]
            )
            logger.info(
                f"[{MATMASTER_AGENT_NAME}]:[{self.name}] context_messages = {context_messages}"
            )

            prompt = gen_params_check_completed_agent_instruction().format(
                context_messages=context_messages
            )
            response = litellm.completion(
                model='azure/gpt-4o',
                messages=[{'role': 'user', 'content': prompt}],
                response_format=ParamsCheckComplete,
            )
            params_check_completed_json: dict = json.loads(
                response.choices[0].message.content
            )
            logger.info(
                f"[{MATMASTER_AGENT_NAME}]:[{self.name}] params_check_completed_json = {params_check_completed_json}"
            )
            params_check_completed = params_check_completed_json['flag']
            params_check_reason = params_check_completed_json['reason']
            params_check_msg = params_check_completed_json['analyzed_messages']

            # 包装成function_call，来避免在历史记录中展示；同时模型可以在上下文中感知
            for params_check_reason_event in context_function_event(
                ctx,
                self.name,
                'system_params_check_result',
                {
                    'complete': params_check_completed,
                    'reason': params_check_reason,
                    'analyzed_messages': params_check_msg,
                },
                ModelRole,
            ):
                yield params_check_reason_event

            if not params_check_completed:
                # Call ParamsCheckInfoAgent to generate params needing check
                async for (
                    params_check_info_event
                ) in self.params_check_info_agent.run_async(ctx):
                    yield params_check_info_event
            else:
                async for tool_call_info_event in self.tool_call_info_agent.run_async(
                    ctx
                ):
                    yield tool_call_info_event
                async for submit_event in self.submit_agent.run_async(ctx):
                    yield submit_event
