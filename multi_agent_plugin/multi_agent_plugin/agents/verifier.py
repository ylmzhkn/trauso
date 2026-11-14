from ..contracts import AgentId
from .base import Agent


class VerifierAgent(Agent):
    agent_id = AgentId.VERIFIER

    async def handle(self, task, context):
        # Deliberately ignores agent reports and internal logs; source adapter is required.
        return {"status": "source_inspection_required", "authoritative_requirement": task.original_prompt,
                "note": "Verification requires read-only access to the actual changed source files."}
