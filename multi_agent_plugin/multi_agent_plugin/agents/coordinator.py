from ..contracts import AgentId
from .base import Agent


class CoordinatorAgent(Agent):
    agent_id = AgentId.COORDINATOR

    async def handle(self, task, context):
        # Decomposition is deliberately conservative until an LLM adapter is configured.
        return {"task_id": str(task.task_id), "status": "needs_decomposition",
                "original_prompt": task.original_prompt,
                "note": "No model provider is configured; no subtasks were fabricated."}
