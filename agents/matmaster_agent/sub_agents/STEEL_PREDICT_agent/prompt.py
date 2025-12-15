STEELPredictAgentName = 'STEEL_PREDICT_agent'

STEELPredictAgentDescription = (
    'Stainless steel tensile strength prediction agent using neural network models. '
    'Predicts ultimate tensile strength (UTS) based on chemical composition. '
    'Supports batch prediction for efficient analysis of multiple formulas.'
)

STEELPredictAgentToolDescription = """
Stainless steel tensile strength prediction tool using neural network models. 

**When to use this tool:**
- Predicting ultimate tensile strength (UTS) for stainless steel based on chemical composition
- Supports batch prediction for efficient analysis of multiple formulas
- Use when you need to predict or analyze tensile strength for stainless steel compositions
- Use for systematic composition variation analysis (e.g., analyzing effect of element variation on strength)
"""

STEELPredictAgentArgsSetting = """
## PARAMETER CONSTRUCTION GUIDE

**Tool:** predict_tensile_strength(formula)

**Parameters:**
- formula (list[str], required): List of chemical formula strings
  - **IMPORTANT**: Always provide a list, even for a single formula
  - Format: ElementSymbol followed by numeric value
  - Example (single): ["Fe70Cr20Ni10"] means Fe=70%, Cr=20%, Ni=10%
  - Example (single): ["C0.1Si0.5Mn1.0Cr18.0Ni8.0"] means C=0.1%, Si=0.5%, Mn=1.0%, Cr=18.0%, Ni=8.0%
  - Example (batch): ["Fe70Cr20Ni10", "Fe68Cr22Ni10", "Fe66Cr24Ni10"] for multiple predictions

**Allowed Elements:**
B, C, N, O, Al, Si, P, S, Ti, V, Cr, Mn, Fe, Co, Ni, Cu, Nb, Mo, W

**Examples:**
1) Predict tensile strength for a single formula (use list with one element):
   → Tool: predict_tensile_strength
     formula: ["Fe70Cr20Ni10"]
   Returns: [650.25] (list with one value)

2) Predict tensile strength with specific composition:
   → Tool: predict_tensile_strength
     formula: ["C0.1Si0.5Mn1.0Cr18.0Ni8.0"]
   Returns: [680.50] (list with one value)

3) Batch prediction for multiple formulas (more efficient):
   → Tool: predict_tensile_strength
     formula: ["Fe70Cr20Ni10", "Fe68Cr22Ni10", "Fe66Cr24Ni10", "Fe64Cr26Ni10"]
   Returns: [650.25, 680.50, 695.30, 710.15]
   This is especially useful when analyzing the effect of element variation on strength.

4) Systematic composition variation analysis:
   → Tool: predict_tensile_strength
     formula: ["Fe66Cr16Ni12Mo2.5", "Fe64Cr18Ni12Mo2.5", "Fe62Cr20Ni12Mo2.5", "Fe60Cr22Ni12Mo2.5"]
   Returns: [620.30, 650.25, 680.50, 710.15]
   Use this to analyze how changing Cr content affects tensile strength.

**Usage Guidelines:**
- **CRITICAL**: Always provide formula as a list, even for a single formula: ["Fe70Cr20Ni10"] not "Fe70Cr20Ni10"
- Always provide the chemical formula in the correct format
- Ensure all elements in the formula are from the allowed set
- The tool will automatically handle element ordering and normalization
- If prediction fails, check the formula format and element names
- The model uses standardized input features, so the tool handles data preprocessing automatically
- **For systematic analysis**: Use batch prediction when analyzing element variation effects (e.g., changing Cr from 16% to 22%)
- **Batch prediction is more efficient**: When predicting multiple formulas, include all in one list
"""

STEELPredictAgentSummaryPrompt = """
## RESPONSE FORMAT

**Returns:**
- List of float values: List of predicted tensile strength values in MPa
- The order matches the input formula list
- Example: [650.25, 680.50, 695.30] for three formulas
- For single formula: Returns a list with one value, e.g., [650.25]

**Presentation Guidelines:**
- Present results clearly to the user:
  - For single formula: "预测结果: 650.25 MPa"
  - For batch: Create a table or list showing formula → prediction mapping
- If the user asks for interpretation, explain what the predicted value(s) mean in context
- For batch results, analyze trends (e.g., "As Cr content increases from 16% to 22%, predicted strength increases from 620.30 to 710.15 MPa")
- Compare with typical stainless steel tensile strength ranges if relevant (e.g., 300-800 MPa for common grades)
- When presenting batch results, organize them in a clear format (table, list, or trend analysis)
- Match each prediction value with its corresponding formula from the input list
"""
