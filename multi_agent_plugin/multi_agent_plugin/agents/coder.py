from ..contracts import AgentId
from .base import Agent


class CoderAgent(Agent):
    agent_id = AgentId.CODER

    async def handle(self, task, context):
        return {"status": "workspace_adapter_required", "scope": task.original_prompt,
                "note": "No filesystem or execution tools are exposed by this scaffold."}
