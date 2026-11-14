from ..contracts import AgentId
from ..policy import Capability, PolicyEngine
from .base import Agent


class TesterAgent(Agent):
    agent_id = AgentId.TESTER

    def __init__(self, policy: PolicyEngine) -> None:
        self.policy = policy

    async def handle(self, task, context):
        approved = bool(context.get("user_test_approval", False))
        self.policy.authorize(self.agent_id, Capability.TEST_EXECUTION, user_approved=approved)
        return {"status": "execution_adapter_required", "task_id": str(task.task_id)}
