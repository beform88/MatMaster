import json

from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event, EventActions

from agents.matmaster_agent.model import JobResult, JobResultType


def is_json(json_str):
    try:
        json.loads(json_str)
    except:
        return False
    return True


async def is_tuple_float(data) -> bool:
    return isinstance(data, tuple) and all(isinstance(x, float) for x in data)


async def is_matmodeler_file(filename: str) -> bool:
    return (filename.endswith((".cif", ".poscar", ".contcar", ".vasp", ".xyz",
                               ".mol", ".mol2", ".sdf", ".dump", ".lammpstrj")) or
            filename.startswith("lammpstrj") or
            "POSCAR" in filename or
            "CONTCAR" in filename or
            filename == "STRU")


async def update_session_state(ctx: InvocationContext, author: str):
    actions_with_update = EventActions(state_delta=ctx.session.state)
    system_event = Event(invocation_id=ctx.invocation_id, author=author, actions=actions_with_update)
    await ctx.session_service.append_event(ctx.session, system_event)


async def parse_result(result: dict):
    # 添加空值检查
    if result is None:
        return [{"status": "error", "msg": "Result is None or invalid"}]

    parsed_result = []
    for k, v in result.items():
        if type(v) in [int, float]:
            parsed_result.append(JobResult(name=k, data=v, type=JobResultType.Value).model_dump(mode="json"))
        elif type(v) == str:
            if not v.startswith("http"):
                parsed_result.append(JobResult(name=k, data=v, type=JobResultType.Value).model_dump(mode="json"))
            else:
                filename = v.split("/")[-1]
                if await is_matmodeler_file(filename):
                    parsed_result.append(JobResult(name=k, data=filename,
                                                   type=JobResultType.MatModelerFile, url=v).model_dump(mode="json"))
                else:
                    parsed_result.append(JobResult(name=k, data=filename,
                                                   type=JobResultType.RegularFile, url=v).model_dump(mode="json"))
        elif await is_tuple_float(v):
            parsed_result.append(JobResult(name=k, data=f"{tuple([float(item) for item in v])}",
                                           type=JobResultType.Value).model_dump(mode="json"))
        else:
            parsed_result.append({"status": "error", "msg": f"{k}({type(v)}) is not supported parse"})
    return parsed_result
