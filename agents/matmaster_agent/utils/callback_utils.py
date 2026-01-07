import logging
import os
from typing import Union

from google.adk.agents import InvocationContext
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools import ToolContext

from agents.matmaster_agent.config import USER_DIRECT_CONSUME
from agents.matmaster_agent.constant import (
    FRONTEND_STATE_KEY,
    MATERIALS_ACCESS_KEY,
    MATERIALS_PROJECT_ID,
    MATMASTER_AGENT_NAME,
)
from agents.matmaster_agent.logger import PrefixFilter
from agents.matmaster_agent.services.project import get_project_list
from agents.matmaster_agent.utils.helper_func import (
    check_None_wrapper,
    get_session_state,
)

logger = logging.getLogger(__name__)
logger.addFilter(PrefixFilter(MATMASTER_AGENT_NAME))
logger.setLevel(logging.INFO)


@check_None_wrapper
async def _get_projectId(ctx: Union[InvocationContext, ToolContext]):
    if USER_DIRECT_CONSUME:
        session_state = get_session_state(ctx)
        project_id = session_state[FRONTEND_STATE_KEY]['biz'].get(
            'projectId'
        ) or os.getenv('BOHRIUM_PROJECT_ID')
        project_list = await get_project_list(access_key=_get_ak(ctx))
        if project_id in project_list:
            return project_id
        else:
            logger.warning(
                f'{ctx.session.id} project_id <{project_id}> is not exist, use project_list[0] <{project_list[0]}>'
            )
            return project_list[0]
    else:
        return MATERIALS_PROJECT_ID


@check_None_wrapper
def _get_ak(ctx: Union[InvocationContext, ToolContext, CallbackContext]):
    if USER_DIRECT_CONSUME:
        session_state = get_session_state(ctx)
        return session_state[FRONTEND_STATE_KEY]['biz'].get('ak') or os.getenv(
            'BOHRIUM_ACCESS_KEY'
        )
    else:
        return MATERIALS_ACCESS_KEY
