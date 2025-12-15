SSEKbAgentName = 'SSEkb_agent'

SSEKbAgentToolDescription = """
Literature knowledge base query tool with structured database search capabilities.

**When to use this tool:**
- Querying materials science literature using structured database queries
- Supports queries based on material properties and paper metadata
- Multi-table queries with complex filters
- Returns literature summaries for comprehensive report generation
- Use when you need structured search across materials science literature
"""

SSEKbAgentArgsSetting = """
## PARAMETER CONSTRUCTION GUIDE

**Tool:** query_ssekb_literature(query_description)

**Parameters:**
- query_description (str, required): Natural language description of the query

**Examples:**
1) 查询特定材料属性：
   → Tool: query_ssekb_literature
     query_description: '查找具有特定性能的材料相关论文'

2) 查询特定材料类型：
   → Tool: query_ssekb_literature
     query_description: '查找特定材料类型的相关论文'
"""

SSEKbAgentSummaryPrompt = """
## TOOL OUTPUT

The tool returns:
- **summaries**: List of literature summaries and database entries (List[str])
  - Each item can be either:
    - A detailed literature summary (for papers with fulltext): Contains comprehensive analysis of the paper
    - A database entry (for papers without fulltext): Contains DOI and database properties (e.g., material properties, experimental data, etc.)
  - These summaries and entries are RAW MATERIALS - you must synthesize them into a comprehensive report
- **code**: Status code
  - 0: Success (summaries available)
  - 1: No results found
  - 2: Cannot read literature fulltext
  - 4: Other errors

## RESPONSE FORMAT

**CRITICAL**: The tool returns RAW summaries and database entries. You MUST synthesize them into a comprehensive, in-depth research report.
**DO NOT simply list or concatenate the summaries - synthesize them into a unified, coherent narrative.**

**IMPORTANT**: The summaries list may contain two types of entries:
1. **Detailed literature summaries** (from papers with fulltext): These contain comprehensive analysis
2. **Database entries** (from papers without fulltext): These contain DOI and database properties (e.g., material properties, experimental data, etc.)

**YOU MUST**:
- Include BOTH types of entries in your synthesis
- For database entries, extract and cite the quantitative data (properties, values, DOI)
- Integrate database property data into your analysis (e.g., compare property ranges, identify trends)
- Cite database entries using their DOI: [n] (DOI: xxx)
- Do NOT ignore database entries - they provide valuable quantitative data even without full text

## EXPRESSION STYLE:
- Tone: Academic, rational, but enlightening
- Expression: Clear, layered, without introducing irrelevant content
- Avoid hollow summaries: Each claim must be explicitly supported by facts, numerical data, or methodological details from the summaries
- Include analytical depth: Provide comparisons, contradictions, or confirmations between studies whenever relevant
- If the user's question is open-ended, provide thorough analysis including:
    1. Mechanistic insights (reaction pathways, driving forces, structure-property relationships)
    2. Quantitative or semi-quantitative results (material names, numerical data, performance metrics, space groups, etc.)
    3. Inconsistencies, limitations, or gaps in current research
- Do not over-emphasize technical details (instrumental settings or computational software and parameter settings) unless necessary

## FORMAT INSTRUCTIONS:
- Output in plain text with clear section headers (##, ###), no bullet points unless necessary
- Avoid statements without evidence from the summaries (e.g., "the first", "the best", "most popular")
- Add space between figures and units (e.g., 10 cm, 5 kg)
- Use italic font for physical quantities (e.g., *E*, *T*, *k*)
- Use bold font for vectors (e.g., **F**, **E**) and serial code names of compounds/materials (e.g., compound **1**)
- Define abbreviations at first use and use consistently throughout
- Cite sources using [1], [2], [3] format (number refers to summary order) throughout the text

## REPORT STRUCTURE:
1. **Introduction**: Professional definition of key concepts, key breakthroughs in recent years, main challenges that remain unsolved, number of papers analyzed (including both detailed summaries and database entries)

2. **Main Content**: Organize into logical sections with subsections (##, ###). For each section:
   - Integrate findings from multiple summaries AND database entries with detailed explanations
   - Include specific quantitative data from both detailed summaries and database entries
   - **For database entries**: Extract and cite property data (e.g., material properties, experimental values, DOI)
   - **Use database entries for statistical analysis**: Group by material type or property type, calculate property ranges, identify trends, create property distributions
   - Use database entries to provide statistical overviews, property ranges, and material comparisons
   - Explain mechanisms and processes in depth (HOW things work, not just WHAT happens)
   - Compare findings across studies, highlighting agreements and disagreements
   - Use tables to compare data from different studies when applicable (include data from database entries)
   - Address contradictions or gaps in current understanding
   - **CRITICAL**: Database entries provide valuable quantitative data - always cite them with their DOI, even if they lack full text context

3. **Property Data Summary** (if database entries are present):
   - Create a dedicated section summarizing quantitative data from database entries
   - Group entries by material type or property type
   - Present property ranges, typical values, and distributions
   - Use tables to organize property data from multiple database entries
   - Cite each database entry: [n] (DOI: xxx)

4. **Summary of Key Findings**: Synthesize the most important insights from both detailed summaries and database entries

5. **References**: List all cited sources [1], [2], [3], etc.
   - For detailed summaries: Include title, authors, journal if available
   - For database entries: Format as [n] DOI: xxx (database entry - property data only)
   - **CRITICAL**: Do NOT omit database entries from references - they are valid data sources and must be cited
"""
