from ..contracts import AgentId
from .base import Agent


class ResearcherAgent(Agent):
    agent_id = AgentId.RESEARCHER

    async def handle(self, task, context):
        return {"status": "adapter_required", "scope": task.original_prompt,
                "note": "Connect an approved web-search provider to enable research."}
