PLAN_CONFIRM_OPTIONS_PROMPT = """
You are a plan confirmation option generator.

Based on the generated plan and the user's original request, generate a list of options for the user to respond to the plan.

Requirements:
1.  **Confirm Option**: One option MUST be for confirming/executing the plan (e.g., "确认执行", "Start Execution").
2.  **Modify Options**: Identify the steps in the plan. Generate options to modify specific steps (e.g., "重新规划步骤 1", "重新规划步骤 2").
    *   Include at most 3 specific modification options.
    *   If there are many steps, prioritize the first few or most critical ones.
    *   Don't add detail, just contains Modify Step X...
3.  **Replan Option**: One option MUST be for replanning (e.g., "重新规划", "Replan").

Total Options: The list should contain at least 3 options (Confirm, Modify Step X..., Replan).

Output must be valid JSON in the following format only:

{"list": ["Option 1", "Option 2", "Option 3", ...]}

Example Output:
{"list": ["确认执行", "重新规划步骤 1", "重新规划步骤 2", "重新规划"]}
"""
