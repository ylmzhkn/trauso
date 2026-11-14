"""Minimal orchestrator facade; persistence and provider adapters are extension points."""
from .contracts import AgentId, TaskStatus
from .task_manager import TaskManager
from .watchdog import Watchdog

class Orchestrator:
    def __init__(self, tasks: TaskManager, watchdog: Watchdog) -> None:
        self.tasks, self.watchdog = tasks, watchdog

    def submit(self, original_prompt: str):
        task = self.tasks.create(original_prompt)
        return self.tasks.transition(task.task_id, TaskStatus.QUEUED)

    def assign(self, task_id, agent_id: AgentId):
        return self.tasks.transition(task_id, TaskStatus.ASSIGNED, assigned_agent=agent_id)
