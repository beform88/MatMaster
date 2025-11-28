PLAN_EXECUTION_CHECK_INSTRUCTION = """
Summarize the executed plan in one sentence. If this is the final step of a plan, end the summary without providing next steps; If not the final step, state the next action using an imperative statement.

If the recent step involved parameter confirmation, display those parameters.
If it involved submitting a task, instruct the user to monitor the task status and specify what to do after completion.

# Specific Requirements:
- When and only when involving research paper results from `search-papers`-related tools, output the **EXACT RAW RESULTS directly without additional commentary** from `msg` of `matmaster_sync_mcp_event`.
"""
