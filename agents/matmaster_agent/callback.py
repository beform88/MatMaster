from datetime import datetime
from typing import Optional

from google.adk.agents.callback_context import CallbackContext
from google.genai import types

try:
    from app.utils.constants import FRONTEND_STATE_KEY
except:
    from agents.matmaster_agent.constants import FRONTEND_STATE_KEY


async def matmaster_before_agent(callback_context: CallbackContext) -> Optional[types.Content]:
    callback_context.state[FRONTEND_STATE_KEY] = callback_context.state.get(FRONTEND_STATE_KEY, {})
    callback_context.state[FRONTEND_STATE_KEY]['biz'] = callback_context.state[FRONTEND_STATE_KEY].get('biz', {})
    callback_context.state['target_language'] = "zh"
    callback_context.state['current_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    callback_context.state["long_running_ids"] = callback_context.state.get("long_running_ids", [])
    callback_context.state["long_running_jobs"] = callback_context.state.get("long_running_jobs", {})
    callback_context.state["render_job_list"] = callback_context.state.get("render_job_list", False)
    callback_context.state["render_job_id"] = callback_context.state.get("render_job_id", [])
    callback_context.state["dflow"] = callback_context.state.get("dflow", False)
    callback_context.state["ak"] = callback_context.state.get("ak", None)
    callback_context.state["project_id"] = callback_context.state.get("project_id", None)
