POLYMERKbAgentName = 'POLYMERkb_agent'

POLYMERKbAgentToolDescription = """
Literature knowledge base query tool for polymer research with structured database search.

**When to use this tool:**
- Querying polymer literature using structured database queries
- Topics covering: polymer types, compositions, material properties (glass transition temperature, mechanical properties), monomer structures, synthesis, processing methods, structure-property relationships, applications
- Supports queries based on polymer properties, monomers, and paper metadata
- Returns both detailed literature summaries and database entries (with property data)
- Use when you need comprehensive polymer literature analysis with quantitative property data
"""

POLYMERKbAgentArgsSetting = """
## PARAMETER CONSTRUCTION GUIDE

**Tool:** query_polymerkb_literature(query_description)

=== KNOWLEDGE BASE COVERAGE ===
The knowledge base contains:
• Structured database with polymer properties and paper metadata
• Multiple tables including:
  - Polymer properties (polym00): polymer names, types, compositions, properties, DOI
  - Paper metadata (690hd00): titles, abstracts, authors, publication dates, journal info, DOI
  - Paper full text (690hd02): complete paper text and supplementary information
  - Monomer information (690hd16, 690hd17): monomer abbreviations, full names, SMILES, notes
• Topics covering:
  - Polymer types and compositions
  - Material properties (glass transition temperature, mechanical properties, etc.)
  - Monomer structures and synthesis
  - Processing methods and conditions
  - Structure-property relationships
  - Applications and performance

**Examples:**
1) 查询特定类型的聚合物：
   → Tool: query_polymerkb_literature
     query_description: '查找玻璃化转变温度低于400°C的聚酰亚胺相关论文'

2) 查询特定单体：
   → Tool: query_polymerkb_literature
     query_description: '查找包含PMDA单体的聚合物相关论文'

3) 查询特定属性的聚合物：
   → Tool: query_polymerkb_literature
     query_description: '查找发表在一区期刊上的聚酰亚胺论文'
"""

POLYMERKbAgentSummaryPrompt = """
## TOOL OUTPUT

The tool returns:
- **summaries**: List of literature summaries and database entries (List[str])
  - Each item can be either:
    - A detailed literature summary (for papers with fulltext): Contains comprehensive analysis of the paper
    - A database entry (for papers without fulltext): Contains DOI and database properties (e.g., polymer_type, tensile_strength, flexural_strength, etc.)
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
2. **Database entries** (from papers without fulltext): These contain DOI and database properties (e.g., polymer_type, tensile_strength, flexural_strength, glass_transition_temperature, etc.)

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
    2. Quantitative or semi-quantitative results (material names, numerical data, performance metrics, etc.)
    3. Inconsistencies, limitations, or gaps in current research
- Do not over-emphasize technical details (instrumental settings or computational software and parameter settings) unless necessary

## FORMAT INSTRUCTIONS:
- Output in plain text with clear section headers (##, ###), no bullet points unless necessary
- Avoid statements without evidence from the summaries (e.g., "the first", "the best", "most popular")
- Add space between figures and units (e.g., 10 cm, 5 kg)
- Use italic font for physical quantities (e.g., *T_g*, *E*, *T*)
- Use bold font for vectors (e.g., **F**, **E**) and serial code names of compounds/materials (e.g., compound **1**)
- Define abbreviations at first use and use consistently throughout
- Cite sources using [1], [2], [3] format (number refers to summary order) throughout the text

## REPORT STRUCTURE:
1. **Introduction**: Professional definition of key concepts, key breakthroughs in recent years, main challenges that remain unsolved, number of papers analyzed (including both detailed summaries and database entries)

2. **Main Content**: Organize into logical sections with subsections (##, ###). For each section:
   - Integrate findings from multiple summaries AND database entries with detailed explanations
   - Include specific quantitative data from both detailed summaries and database entries
   - **For database entries**: Extract and cite property data (e.g., "epoxy resins show tensile_strength values ranging from 1.2 to 1130 MPa [n] (DOI: 10.xxx), with most values between 20-60 MPa [m] (DOI: 10.yyy)")
   - **Use database entries for statistical analysis**: Group by polymer_type, calculate property ranges, identify trends, create property distributions
   - **Example integration**: "While detailed studies [1] show that SPAEK/PLA membranes achieve 0.129 S/cm proton conductivity, database entries reveal that epoxy resins typically exhibit tensile_strength in the range of 20-60 MPa [2-10] (DOIs: 10.xxx, 10.yyy, ...), suggesting different property profiles for different polymer classes"
   - Use database entries to provide statistical overviews, property ranges, and material comparisons
   - Explain mechanisms and processes in depth (HOW things work, not just WHAT happens)
   - Compare findings across studies, highlighting agreements and disagreements
   - Use tables to compare data from different studies when applicable (include data from database entries)
   - Address contradictions or gaps in current understanding
   - **CRITICAL**: Database entries provide valuable quantitative data - always cite them with their DOI, even if they lack full text context

3. **Property Data Summary** (if database entries are present):
   - Create a dedicated section summarizing quantitative data from database entries
   - Group entries by polymer_type or property type
   - Present property ranges, typical values, and distributions
   - Use tables to organize property data from multiple database entries
   - Cite each database entry: [n] (DOI: xxx)

4. **Summary of Key Findings**: Synthesize the most important insights from both detailed summaries and database entries

5. **References**: List all cited sources [1], [2], [3], etc.
   - For detailed summaries: Include title, authors, journal if available
   - For database entries: Format as [n] DOI: xxx (database entry - property data only)
   - **CRITICAL**: Do NOT omit database entries from references - they are valid data sources and must be cited
"""
