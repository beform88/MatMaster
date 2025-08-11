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


async def is_float_sequence(data) -> bool:
    return isinstance(data, (tuple, list)) and all(isinstance(x, float) for x in data)


async def is_str_sequence(data) -> bool:
    return isinstance(data, (tuple, list)) and all(isinstance(x, str) for x in data)


async def is_matmodeler_file(filename: str) -> bool:
    return (filename.endswith((".cif", ".poscar", ".contcar", ".vasp", ".xyz",
                               ".mol", ".mol2", ".sdf", ".dump", ".lammpstrj")) or
            filename.startswith("lammpstrj") or
            "POSCAR" in filename or
            "CONTCAR" in filename or
            filename == "STRU")


async def is_image_file(filename: str) -> bool:
    return (filename.endswith((".png", ".jpg", ".jpeg")))


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
    """
    Parse and flatten a nested dictionary result into a list of standardized JobResult objects.

    Processes a dictionary (potentially nested) and converts it into serialized JobResult objects.
    Handles various data types including numbers, strings, sequences, and file URLs.
    For image URLs, automatically generates both file reference and markdown representation.

    Args:
        result (dict): Input dictionary to parse. May contain:
                      - Nested dictionaries (automatically flattened)
                      - Primitive values (int, float, str)
                      - Sequences (of numbers or strings)
                      - URLs (regular files or MatModeler files)

    Returns:
        list: Serialized JobResult objects with appropriate types:
              - Value: For primitive types and sequences
              - MatModelerFile/RegularFile: For recognized file URLs
              - Additional markdown representation for image files
              - Error messages for unsupported types

    Example:
        >>> parse_result({"value": 42, "structure": "http://example.com/structure.cif", "phonon": "http://example.com/phonon.png"})

        >>> [
        >>>    {"name": "value", "data": 42, "type": "Value"},
        >>>    {"name": "structure", "data": "structure.cif", "type": "MatModelerFile", "url": "http://example.com/structure.cif"},
        >>>    {"name": "phonon", "data": "phonon.png", "type": "RegularFile", "url": "http://example.com/phonon.png"}
        >>>    {"name": "markdown_image_phonon", "data": "![phonon.png](http://example.com/phonon.png)", "type": "Value"}
        >>> ]
    """
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
                if await is_image_file(filename):
                    # Extra Add Markdown Image
                    parsed_result.append(JobResult(name=f"markdown_image_{k}", data=f"![{filename}]({v})",
                                                   type=JobResultType.Value).model_dump(mode="json"))
        elif await is_float_sequence(v):
            parsed_result.append(JobResult(name=k, data=f"{tuple([float(item) for item in v])}",
                                           type=JobResultType.Value).model_dump(mode="json"))
        elif await is_str_sequence(v):
            parsed_result.append(JobResult(name=k, data=f"{tuple([str(item) for item in v])}",
                                           type=JobResultType.Value).model_dump(mode="json"))
        else:
            parsed_result.append({"status": "error", "msg": f"{k}({type(v)}) is not supported parse, v={v}"})
    return parsed_result
