import os
from typing import Union

from google.adk.agents import InvocationContext
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools import ToolContext

from agents.matmaster_agent.constant import FRONTEND_STATE_KEY
from agents.matmaster_agent.utils.helper_func import (
    check_None_wrapper,
    get_session_state,
)


@check_None_wrapper
def _get_projectId(ctx: Union[InvocationContext, ToolContext]):
    session_state = get_session_state(ctx)
    return session_state[FRONTEND_STATE_KEY]['biz'].get('projectId') or os.getenv(
        'BOHRIUM_PROJECT_ID'
    )


@check_None_wrapper
def _get_ak(ctx: Union[InvocationContext, ToolContext, CallbackContext]):
    session_state = get_session_state(ctx)
    return session_state[FRONTEND_STATE_KEY]['biz'].get('ak') or os.getenv(
        'BOHRIUM_ACCESS_KEY'
    )
