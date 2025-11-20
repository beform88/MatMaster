from agents.matmaster_agent.constant import CURRENT_ENV

DocumentParserAgentName = 'document_parser_agent'

if CURRENT_ENV in ['test', 'uat']:
    DocumentParserServerUrl = 'http://pfmx1355864.bohrium.tech:50005/sse'
else:
    DocumentParserServerUrl = 'https://document-parser-uuid1758175282.appspace.bohrium.com/sse?token=1b824a883cff4af1b1c8345d3bc693d5'
