from ..contracts import AgentId
from .base import Agent


class AnalystAgent(Agent):
    agent_id = AgentId.ANALYST

    async def handle(self, task, context):
        return {"status": "workspace_adapter_required", "scope": task.original_prompt,
                "note": "A sandboxed, read-only workspace adapter must be configured."}
