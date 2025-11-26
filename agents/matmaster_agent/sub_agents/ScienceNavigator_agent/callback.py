import json

from mcp.types import CallToolResult, TextContent


async def after_tool_callback(tool, args, tool_context, tool_response):
    print(f"[after_tool_callback] Tool '{tool.name}' executed.")
    print(type(tool_response))
    tool_output = tool_response.content
    try:
        output_json = json.loads(tool_output[0].text)
        output_paper_list = output_json['data']
    except Exception as e:
        print(e)
        return tool_response
    DISCARD_KEYS = [
        'paperId',
        'publicationId',
        'publicationCover',
        'zhName',
        'zhAbstract',
        'languageType',
        'popularity',
        'goodFlag',
        'readFlag',
        'addFlag',
        'graphicalAbstract',
        'openAccess',
        'pdfFlag',
        'title',
        'authorDetails',
        'alltext',
    ]

    filtered_papers = []
    for paper_info in output_paper_list:
        new_info = {k: v for k, v in paper_info.items() if k not in DISCARD_KEYS}
        filtered_papers.append(new_info)

    new_content = json.dumps({'data': filtered_papers})

    new_response = CallToolResult(
        content=[TextContent(type='text', text=new_content)],
        meta=getattr(tool_response, 'meta', None),
    )

    return new_response
