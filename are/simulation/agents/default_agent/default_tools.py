# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the terms described in the LICENSE file in
# the root directory of this source tree.


import json
import textwrap

from are.simulation.tool_box import get_tool_description_with_args
from are.simulation.tools import Tool

TOOL_SYSTEM_PROMPT_TEMPLATE = textwrap.dedent(
    """
    {tools}
    """
)


def generate_tool_description(tools: list[Tool]) -> str:
    tool_desc = "\n".join([get_tool_description_with_args(tool) for tool in tools])
    return TOOL_SYSTEM_PROMPT_TEMPLATE.format(tools=tool_desc)


class FinalAnswerTool(Tool):
    name = "final_answer"
    description = "Provides a final answer to the given problem. MUST be called in accordance with the formatting specification in the thought-action format"
    inputs = {
        "answer": {"type": "any", "description": "The final answer to the problem"}
    }
    output_type = "any"

    def forward(self, answer):
        # Normalize the answer to always return a string
        # This ensures compatibility with _append_final_answer which expects string or MMObservation
        if isinstance(answer, str):
            return answer
        elif isinstance(answer, (dict, list)):
            # Convert structured data to JSON string for readability
            return json.dumps(answer, indent=2, ensure_ascii=False)
        elif answer is None:
            return ""
        else:
            # Convert any other type (numbers, booleans, etc.) to string
            return str(answer)
