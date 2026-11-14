from ..contracts import AgentId
from .base import Agent


class RepairAgent(Agent):
    agent_id = AgentId.REPAIR

    async def handle(self, task, context):
        error = context.get("concrete_error")
        if not error:
            return {"status": "no_change", "reason": "Repair requires a concrete reported error."}
        return {"status": "scoped_repair_adapter_required", "concrete_error": str(error),
                "affected_files": context.get("affected_files", [])}
