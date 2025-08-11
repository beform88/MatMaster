import json

from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event, EventActions

from agents.matmaster_agent.model import JobResult, JobResultType


async def update_session_state(ctx: InvocationContext, author: str):
    actions_with_update = EventActions(state_delta=ctx.session.state)
    system_event = Event(invocation_id=ctx.invocation_id, author=author, actions=actions_with_update)
    await ctx.session_service.append_event(ctx.session, system_event)


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


def flatten_dict(d, parent_key='', sep='_'):
    """
    将多层嵌套的字典拉平为一级字典

    参数:
        d: 要拉平的字典
        parent_key: 父级键名(递归时使用)
        sep: 嵌套键之间的分隔符

    返回:
        拉平后的一级字典
    """
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        elif isinstance(v, list):
            # 处理列表中的字典项
            for i, item in enumerate(v):
                if isinstance(item, dict):
                    items.extend(flatten_dict(item, f"{new_key}{sep}{i}", sep=sep).items())
                else:
                    items.append((f"{new_key}{sep}{i}", item))
        else:
            items.append((new_key, v))
    return dict(items)


async def parse_result(result: dict):
    parsed_result = []
    new_result = {}
    for k, v in result.items():
        if type(v) == dict:
            new_result.update(**flatten_dict(v))
        else:
            new_result[k] = v

    for k, v in new_result.items():
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
            parsed_result.append({"status": "error", "msg": f"{k}({type(v)}) is not supported parse, v={v}"})
    return parsed_result
