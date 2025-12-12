from agents.matmaster_agent.constant import CURRENT_ENV

DocumentParserAgentName = 'document_parser_agent'

if CURRENT_ENV in ['test', 'uat']:
    DocumentParserServerUrl = 'http://pfmx1355864.bohrium.tech:50005/sse'
else:
    # DocumentParserServerUrl = 'https://document-parser-uuid1758175282.appspace.bohrium.com/sse?token=17a3a9849c1c4fde963a7dc1135aca18'
    DocumentParserServerUrl = 'http://pfmx1355864.bohrium.tech:50001/sse'
