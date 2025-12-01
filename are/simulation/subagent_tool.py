from are.simulation.tools import Tool

class SubagentTool(Tool):
    def __init__(self, name, description, delegate):
        self.name = name
        self.description = description
        self.inputs = {
            "task": {
                "type": "string",
                "description": "Task description for this subagent to execute.",
            }
        }
        self.output_type = "string"
        super().__init__()
        self._delegate = delegate
    
    def forward(self, task: str):
        return self._delegate(task)