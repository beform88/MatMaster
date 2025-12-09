import logging
from typing import List, Union

from pydantic import BaseModel

from agents.matmaster_agent.constant import JOB_RESULT_KEY, MATMASTER_AGENT_NAME
from agents.matmaster_agent.logger import PrefixFilter
from agents.matmaster_agent.model import (
    JobResult,
    JobResultType,
    LiteratureItem,
    Matrix,
    RenderTypeEnum,
    WebSearchItem,
)

logger = logging.getLogger(__name__)
logger.addFilter(PrefixFilter(MATMASTER_AGENT_NAME))
logger.setLevel(logging.INFO)


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
                    items.extend(
                        flatten_dict(item, f"{new_key}{sep}{i}", sep=sep).items()
                    )
                else:
                    items.append((f"{new_key}{sep}{i}", item))
        else:
            items.append((new_key, v))
    return dict(items)


async def is_matmodeler_file(filename: str) -> bool:
    return (
        filename.endswith(
            (
                '.cif',
                '.poscar',
                '.contcar',
                '.vasp',
                '.xyz',
                '.mol',
                '.mol2',
                '.sdf',
                '.dump',
                '.lammpstrj',
                '.gro',
                '.trr',
                '.xtc',
            )
        )
        or filename.startswith('lammpstrj')
        or 'POSCAR' in filename
        or 'CONTCAR' in filename
        or filename == 'STRU'
    )


async def is_echarts_file(filename: str) -> bool:
    return filename.endswith('.echarts')


async def is_image_file(filename: str) -> bool:
    return filename.endswith(('.png', '.jpg', '.jpeg', '.svg'))


def is_sequence(data):
    return isinstance(data, (tuple, list))


async def is_float_sequence(data) -> bool:
    return is_sequence(data) and all(isinstance(x, float) for x in data)


async def is_str_sequence(data) -> bool:
    return is_sequence(data) and all(isinstance(x, str) for x in data)


async def is_literature_sequence(data) -> bool:
    return is_sequence(data) and validate_model_list(data, LiteratureItem)


async def is_web_search_sequence(data) -> bool:
    return is_sequence(data) and validate_model_list(data, WebSearchItem)


def is_matrix(data):
    return is_sequence(data) and all(is_sequence(row) for row in data)


async def is_float_matrix(data) -> bool:
    return is_matrix(data) and all(isinstance(x, float) for row in data for x in row)


def validate_model_list(data: list, model: type[BaseModel]) -> bool:
    for item in data:
        try:
            model.model_validate(item)
        except BaseException as e:
            logger.warning(e)
            return False
    return True


async def parse_result(result: dict) -> List[Union[dict, WebSearchItem, JobResult]]:
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
        if type(v) is dict:
            new_result.update(**flatten_dict(v))
        else:
            new_result[k] = v

    for k, v in new_result.items():
        if type(v) in [int, float, bool]:
            parsed_result.append(
                JobResult(name=k, data=v, type=JobResultType.Value).model_dump(
                    mode='json'
                )
            )
        elif type(v) is str:
            if not v.startswith('http'):
                parsed_result.append(
                    JobResult(name=k, data=v, type=JobResultType.Value).model_dump(
                        mode='json'
                    )
                )
            else:
                filename = v.split('/')[-1]
                if await is_matmodeler_file(filename):
                    parsed_result.append(
                        JobResult(
                            name=k,
                            data=filename,
                            type=JobResultType.MatModelerFile,
                            url=v,
                        ).model_dump(mode='json')
                    )
                elif await is_echarts_file(filename):
                    parsed_result.append(
                        JobResult(
                            name=k,
                            data=filename,
                            type=JobResultType.EchartsFile,
                            url=v,
                        ).model_dump(mode='json')
                    )
                else:
                    parsed_result.append(
                        JobResult(
                            name=k, data=filename, type=JobResultType.RegularFile, url=v
                        ).model_dump(mode='json')
                    )
                if await is_image_file(filename):
                    # Extra Add Markdown Image
                    parsed_result.append(
                        JobResult(
                            name=f"markdown_image_{k}",
                            data=f"![{filename}]({v})",
                            type=JobResultType.Value,
                        ).model_dump(mode='json')
                    )
        elif await is_float_sequence(v):
            parsed_result.append(
                JobResult(
                    name=k,
                    data=f"{tuple([float(item) for item in v])}",
                    type=JobResultType.Value,
                ).model_dump(mode='json')
            )
        elif await is_str_sequence(v):
            parsed_result.append(
                JobResult(
                    name=k,
                    data=f"{tuple([str(item) for item in v])}",
                    type=JobResultType.Value,
                ).model_dump(mode='json')
            )
        elif await is_literature_sequence(v):
            for item in v:
                parsed_result.append(LiteratureItem(**item).model_dump(mode='json'))
        elif await is_web_search_sequence(v):
            for item in v:
                parsed_result.append(WebSearchItem(**item).model_dump(mode='json'))
        elif await is_float_matrix(v):
            parsed_result.append(Matrix(title=k, values=v).model_dump(mode='json'))
        else:
            parsed_result.append(
                {
                    'status': 'error',
                    'msg': f"{k}({type(v)}) is not supported parse, v={v}",
                }
            )
    return parsed_result


def get_kv_result(parsed_tool_result: List[dict]):
    return {
        'eventType': 1,
        'eventData': {
            'contentType': 1,
            'renderType': '@bohrium-chat/matmodeler/dialog-file',
            'content': {
                JOB_RESULT_KEY: [
                    item
                    for item in parsed_tool_result
                    if item.get('status', None) is None
                    and item.get('name')
                    and item.get('data')
                    and not (item.get('name') == 'code')
                ]
            },
        },
    }


def get_markdown_image_result(parsed_tool_result: List[JobResult]) -> List[JobResult]:
    return [
        item
        for item in parsed_tool_result
        if item.get('name') and item['name'].startswith('markdown_image')
    ]


def get_echarts_result(parsed_tool_result: List[JobResult]) -> List[JobResult]:
    return [
        item
        for item in parsed_tool_result
        if item.get('name') and item['type'] == JobResultType.EchartsFile
    ]


def get_matrix_result(
    parsed_tool_result: List[Union[JobResult, Matrix]],
) -> List[Matrix]:
    return [
        item
        for item in parsed_tool_result
        if item.get('meta_type') and item['meta_type'] == RenderTypeEnum.MATRIX
    ]


def matrix_to_markdown_table(matrix):
    title, values = matrix['title'], matrix['values']

    if not values:
        return ''

    col_count = len(values[0])
    header = ' | '.join([f"Col{i + 1}" for i in range(col_count)])
    separator = ' | '.join(['---'] * col_count)

    rows = '\n'.join(' | '.join(str(v) for v in row) for row in values)

    table = f"{header}\n{separator}\n{rows}"

    if title:
        return f"- {title}\n\n{table}"
    else:
        return table


if __name__ == '__main__':
    import asyncio

    result = {
        'elastic_tensor': [
            [
                126.67322172600046,
                34.44381584060013,
                26.459989419200095,
                11.290835605200044,
                -7.436680000013668e-05,
                -0.00010517060000019208,
            ],
            [
                34.51137231640013,
                126.57536433180044,
                26.46490396520009,
                -11.249254931600042,
                -0.0008022412000001377,
                -0.002352200200000196,
            ],
            [
                27.197465286400107,
                27.200289148200106,
                133.25489116180051,
                -0.0014687360000000815,
                -0.002543925200000152,
                -0.002445536800000209,
            ],
            [
                10.5314041983,
                -10.607130737500002,
                -0.008035032099999876,
                37.61116754140001,
                0.00012512119999999013,
                0.0013957529999999974,
            ],
            [
                0.0009393182000000179,
                -0.0004212151999997845,
                -0.002185717099999327,
                -0.00031142229999990724,
                38.112387281800004,
                11.281813003800004,
            ],
            [
                0.0015451324000000208,
                -0.0026245466999992575,
                -0.0011686156999995213,
                0.00020765799999999807,
                10.4503386476,
                44.8908194704,
            ],
        ]
    }

    parsed_result = asyncio.run(parse_result(result))
    matrix_result: List[Matrix] = get_matrix_result(parsed_result)

    for matrix in matrix_result:
        markdown_matrix = matrix_to_markdown_table(matrix['title'], matrix['values'])
