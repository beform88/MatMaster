import json
from typing import AsyncGenerator, Optional, override

import litellm
from google.adk.agents import InvocationContext, LlmAgent, SequentialAgent
from google.adk.events import Event
from pydantic import Field

from agents.matmaster_agent.base_agents.callback import remove_function_call
from agents.matmaster_agent.base_agents.job_agent import (
    ParamsCheckInfoAgent,
    ResultCalculationMCPLlmAgent,
    SubmitCoreCalculationMCPLlmAgent,
    SubmitRenderAgent,
    SubmitValidatorAgent,
    ToolCallInfoAgent,
    logger,
)
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
from agents.matmaster_agent.utils.helper_func import get_session_state


class BaseAsyncJobAgent(LlmAgent):
    submit_agent: SequentialAgent
    result_agent: SequentialAgent
    params_check_info_agent: LlmAgent
    tool_call_info_agent: LlmAgent
    dflow_flag: bool = Field(
        False, description='Whether the agent is dflow related', exclude=True
    )
    supervisor_agent: str
    sync_tools: Optional[list] = Field(
        None, description='These tools will sync run on the server'
    )
    enable_tgz_unpack: bool = Field(
        True, description='Whether unpack tgz files for tool_results'
    )

    def __init__(
        self,
        model,
        agent_name: str,
        agent_description: str,
        agent_instruction: str,
        mcp_tools: list,
        dflow_flag: bool,
        supervisor_agent: str,
        sync_tools: Optional[list] = None,
        enable_tgz_unpack: bool = True,
        cost_func: Optional[CostFuncType] = None,
    ):
        agent_prefix = agent_name.replace('_agent', '')

        # 创建提交核心代理
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

        # 创建提交渲染代理
        submit_render_agent = SubmitRenderAgent(
            model=model, name=f"{agent_prefix}_submit_render_agent"
        )

        submit_validator_agent = SubmitValidatorAgent(
            model=model, name=f"{agent_prefix}_submit_validator_agent"
        )

        # 创建提交序列代理
        submit_agent = SequentialAgent(
            name=f"{agent_prefix}_submit_agent",
            description=gen_submit_agent_description(agent_prefix),
            sub_agents=[submit_core_agent, submit_render_agent, submit_validator_agent],
        )

        # 创建结果核心代理
        result_core_agent = ResultCalculationMCPLlmAgent(
            model=model,
            name=f"{agent_prefix}_result_core_agent",
            tools=mcp_tools,
            instruction=gen_result_core_agent_instruction(agent_prefix),
            enable_tgz_unpack=enable_tgz_unpack,
        )

        # 创建结果序列代理
        result_agent = SequentialAgent(
            name=f"{agent_prefix}_result_agent",
            description=gen_result_agent_description(),
            sub_agents=[result_core_agent],
        )

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

        # 初始化父类
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
        )

    @override
    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
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

        for function_event in context_function_event(
            ctx,
            self.name,
            'transfer_to_agent',
            None,
            ModelRole,
            {'agent_name': self.supervisor_agent},
        ):
            yield function_event
