HEAKbAgentName = 'HEAkb_agent'

HEAKbAgentToolDescription = """
Literature knowledge base query tool for HEA (High-Entropy Alloy) research. 

**When to use this tool:**
- Querying HEA literature knowledge base with natural language questions
- Topics covering: phase transformations, mechanical properties, corrosion behavior, microstructure, preparation methods, element selection, strengthening mechanisms, high/low temperature performance, applications, multi-phase structures, lattice distortion effects
- Supports vector similarity search across 1M+ document chunks
- Returns literature summaries for comprehensive report generation
- Use when you need in-depth literature analysis on HEA topics
"""

HEAKbAgentArgsSetting = """
## PARAMETER CONSTRUCTION GUIDE

## Do not ask the user for confirmation; directly start retrieval when a query is made.

**Parameters:**
- question (str, required): Natural language query about HEA research topics
- top_k (int, optional): Number of chunks to retrieve (5-15 recommended, default: 5)

**Examples:**
1) 查询高熵合金中的相变机制：
   → Tool: query_heakb_literature
     question: '高熵合金中的相变诱导塑性（TRIP）机制是什么？这种机制如何影响合金的力学性能？'
     top_k: 5

2) 查询FCC到HCP相变的条件：
   → Tool: query_heakb_literature
     question: '高熵合金中的FCC到HCP相变的条件和影响因素是什么？'
     top_k: 8

3) 查询低温下的力学性能：
   → Tool: query_heakb_literature
     question: '高熵合金在低温下的力学性能如何？影响低温性能的主要因素有哪些？'
     top_k: 10

4) 查询腐蚀行为和防护机制：
   → Tool: query_heakb_literature
     question: '高熵合金的腐蚀行为和防护机制是什么？不同元素对腐蚀性能的影响如何？'
     top_k: 5

5) 查询微观结构特征：
   → Tool: query_heakb_literature
     question: '高熵合金的微观结构特征是什么？如何通过热处理调控微观结构？'
     top_k: 6

6) 查询制备方法：
   → Tool: query_heakb_literature
     question: '高熵合金的主要制备方法有哪些？不同制备方法对合金性能的影响如何？'
     top_k: 7
"""

HEAKbAgentSummaryPrompt = """
## TOOL OUTPUT

The tool returns:
- **summaries**: List of literature summaries (List[str])
  - Each summary is a text string containing the summary of one literature paper
  - These summaries are RAW MATERIALS - you must synthesize them into a comprehensive report
- **code**: Status code
  - 0: Success (summaries available)
  - 1: No results found
  - 2: Cannot read literature fulltext
  - 4: Other errors

## RESPONSE FORMAT

**CRITICAL**: The tool returns RAW summaries. You MUST synthesize them into a comprehensive, in-depth research report.
**DO NOT simply list or concatenate the summaries - synthesize them into a unified, coherent narrative.**

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
1. **Introduction**: Professional definition of key concepts, key breakthroughs in recent years, main challenges that remain unsolved, number of papers analyzed

2. **Main Content**: Organize into logical sections with subsections (##, ###). For each section:
   - Integrate findings from multiple summaries with detailed explanations
   - Include specific quantitative data, experimental conditions, and results
   - Explain mechanisms and processes in depth (HOW things work, not just WHAT happens)
   - Compare findings across studies, highlighting agreements and disagreements
   - Use tables to compare data from different studies when applicable
   - Address contradictions or gaps in current understanding

3. **Summary of Key Findings**: Synthesize the most important insights

4. **References**: List all cited sources [1], [2], [3], etc.
"""
