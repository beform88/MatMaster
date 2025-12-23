from textwrap import dedent


def branching_instruction(branch_id: int, max_depth: int) -> str:
    return dedent(
        f"""
        [Tree-of-Thoughts branch {branch_id}]
        - Generate a distinct and self-contained execution plan that strictly follows the provided JSON schema.
        - Prefer alternative tool combinations, ordering, or decomposition strategies so that each branch explores a different path.
        - Keep the number of steps concise and avoid repeating the same reasoning used in other branches.
        - Depth limit: {max_depth} levels of refinement are available, so focus on high-value ideas first.
        """
    )


def refinement_instruction(previous_plan: str, feedback: str) -> str:
    return dedent(
        f"""
        [Tree-of-Thoughts refinement]
        You are improving an existing candidate plan.
        Current best plan (JSON):
        {previous_plan}

        Feedback to address:
        {feedback}

        Revise the plan to better satisfy the feedback while keeping tool names valid and within the allowed list. Return only the updated JSON plan.
        """
    )


def scoring_instruction(user_query: str, tools_info: str) -> str:
    return dedent(
        f"""
        You are ranking alternative tool-execution plans for the following user request:
        """
        f"{user_query}\n"
        """

        Available tools:
        {tools_info}

        Evaluate the plan JSON on these axes:
        1) Alignment with the user's explicit goals and constraints
        2) Correct tool selection and ordering (no missing or invented tools)
        3) Completeness and minimal redundancy
        4) Feasibility given the inputs (URLs are usable directly)

        Return a JSON object with fields:
        {{
          "score": <int 0-100>,  // Higher is better
          "keep": <true|false>,  // Whether this plan should remain in the beam
          "reasons": [<string>], // Key rationale for the score
          "risks": [<string>]    // Potential failure points or uncertainties
        }}
        """
    )
