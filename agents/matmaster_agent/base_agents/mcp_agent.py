from typing import Callable, Optional

from pydantic import Field

from agents.matmaster_agent.base_agents.callback import (
    catch_after_tool_callback_error,
    catch_before_tool_callback_error,
    check_before_tool_callback_effect,
    check_job_create,
    check_user_phonon_balance,
    default_after_model_callback,
    default_after_tool_callback,
    default_before_tool_callback,
    default_cost_func,
    inject_current_env,
    inject_userId_sessionId,
    inject_username_ticket,
    remove_job_link,
    tgz_oss_to_oss_list,
)
from agents.matmaster_agent.base_agents.subordinate_agent import SubordinateAgent


# LlmAgent -> ErrorHandleAgent -> SubordinateAgent -> MCPLlmAgent
class MCPLlmAgent(SubordinateAgent):
    """An LLM agent specialized for calculation tasks with built-in error handling and project ID management.

    Extends the HandleFileUploadLlmAgent with additional features:
    - Automatic error handling for tool calls
    - Project ID retrieval before tool execution
    - OpikTracer integration for comprehensive operation tracing

    Note: User-provided callbacks will execute before the built-in OpikTracer callbacks.

    Attributes:
        Inherits all attributes from LlmAgent.
    """

    loading: bool = Field(
        False, description='Whether the agent display loading state', exclude=True
    )
    render_tool_response: bool = Field(
        False, description='Whether render tool response in frontend', exclude=True
    )
    enable_tgz_unpack: bool = Field(
        True, description='Whether unpack tgz files for tool_results'
    )
    cost_func: Optional[Callable[[], int]] = None

    def __init__(
        self,
        model,
        name,
        instruction='',
        description='',
        sub_agents=None,
        global_instruction='',
        tools=None,
        output_key=None,
        before_agent_callback=None,
        before_model_callback=None,
        before_tool_callback=default_before_tool_callback,
        after_tool_callback=default_after_tool_callback,
        after_model_callback=default_after_model_callback,
        after_agent_callback=None,
        loading=False,
        render_tool_response=False,
        disallow_transfer_to_parent=False,
        supervisor_agent=None,
        enable_tgz_unpack=True,
        cost_func=default_cost_func,
    ):
        """Initialize a CalculationLlmAgent with enhanced tool call capabilities.

        Args:
            model: The language model instance to be used by the agent
            name: Unique identifier for the agent
            instruction: Primary instruction guiding the agent's behavior
            description: Optional detailed description of the agent (default: '')
            sub_agents: List of subordinate agents (default: None)
            global_instruction: Instruction applied across all agent operations (default: '')
            tools: Tools available to the agent (default: None)
            output_key: Key for identifying the agent's output (default: None)
            before_agent_callback: Callback executed before agent runs (default: None)
            before_model_callback: Callback executed before model inference (default: None)
            before_tool_callback: Callback executed before tool execution
                                (default: default_before_tool_callback)
            after_tool_callback: Callback executed after tool execution (default: None)
            after_model_callback: Callback executed after model inference (default: None)
            after_agent_callback: Callback executed after agent completes (default: None)

        Implementation Notes:
            1. Wraps the before_tool_callback with:
               - Error handling (catch_tool_call_error)
               - Project ID retrieval (get_ak_projectId)
            2. Maintains callback execution order: user callbacks → OpikTracer callbacks
            3. Designed specifically for calculation-intensive MCP workflows
        """

        # Todo: support List[before_tool_callback]
        before_tool_callback = catch_before_tool_callback_error(
            inject_current_env(
                inject_username_ticket(
                    check_job_create(
                        check_user_phonon_balance(
                            inject_userId_sessionId(before_tool_callback), cost_func
                        )
                    )
                )
            )
        )
        after_tool_callback = check_before_tool_callback_effect(
            catch_after_tool_callback_error(
                remove_job_link(
                    tgz_oss_to_oss_list(after_tool_callback, enable_tgz_unpack)
                )
            )
        )

        super().__init__(
            model=model,
            name=name,
            description=description,
            instruction=instruction,
            global_instruction=global_instruction,
            sub_agents=sub_agents or [],
            tools=tools or [],
            output_key=output_key,
            before_agent_callback=before_agent_callback,
            before_model_callback=before_model_callback,
            before_tool_callback=before_tool_callback,
            after_tool_callback=after_tool_callback,
            after_model_callback=after_model_callback,
            after_agent_callback=after_agent_callback,
            disallow_transfer_to_parent=disallow_transfer_to_parent,
            supervisor_agent=supervisor_agent,
            enable_tgz_unpack=enable_tgz_unpack,
        )

        self.loading = loading
        self.render_tool_response = render_tool_response
        self.enable_tgz_unpack = enable_tgz_unpack
