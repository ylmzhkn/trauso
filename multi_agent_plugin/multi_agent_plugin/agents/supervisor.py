from ..contracts import AgentId
from ..watchdog import Watchdog
from .base import Agent


class SupervisorAgent(Agent):
    agent_id = AgentId.SUPERVISOR

    def __init__(self, watchdog: Watchdog) -> None:
        self.watchdog = watchdog

    async def handle(self, task, context):
        findings = {
            agent: self.watchdog.inspect(agent)
            for agent in context.get("active_agents", [])
        }
        return {"task_id": str(task.task_id), "health_findings": {
            key: finding.__dict__ for key, finding in findings.items()
        }}
