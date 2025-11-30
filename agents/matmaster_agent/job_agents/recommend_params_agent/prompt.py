def gen_recommend_params_agent_instruction():
    return """
Convert the recommended parameters into a user-friendly format for a tool invocation.

- The output language must be {target_language}.

## FORMAT INSTRUCTIONS:
- A space should be added between figures and units, e.g. 10 cm, 5 kg. An italic font should be used for physical quantities. A bold font should be used for vectors;
- Chemical formula should be appropriately formatted using superscript and subscript, not plain text;
- Space group should be written in the format of appropriate `H-M` notation with Latin letters in intalics and correct subscript for screw axis, not plain text.

Critical Instructions:
- If the input parameter is a **complete HTTP or HTTPS URL**, use it directly as the parameter.
- Present the information in a clear, readable style, such as a list or natural paragraphs.
- Do not end with any question or prompt for user action.
"""
