from agents.matmaster_agent.constant import CURRENT_ENV

DocumentParserAgentName = "document_parser_agent"

if CURRENT_ENV in ["test", "uat"]:
    DocumentParserServerUrl = "http://pfmx1355864.bohrium.tech:50005/sse"
else:
    DocumentParserServerUrl = "https://document-parser-mcp-uuid1753018122.app-space.dplink.cc/sse?token=e93e98d3c408478d9ff113b809de690d"