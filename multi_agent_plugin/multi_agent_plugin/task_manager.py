"""In-memory task state machine; replace with durable repository adapter for production."""

from datetime import datetime, timezone
from uuid import UUID

from .contracts import TaskRecord, TaskStatus


_ALLOWED: dict[TaskStatus, set[TaskStatus]] = {
    TaskStatus.CREATED: {TaskStatus.QUEUED, TaskStatus.CANCELLED},
    TaskStatus.QUEUED: {TaskStatus.ASSIGNED, TaskStatus.CANCELLED},
    TaskStatus.ASSIGNED: {TaskStatus.RUNNING, TaskStatus.CANCELLED, TaskStatus.FAILED},
    TaskStatus.RUNNING: {TaskStatus.WAITING, TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED},
    TaskStatus.WAITING: {TaskStatus.RUNNING, TaskStatus.FAILED, TaskStatus.CANCELLED},
    TaskStatus.FAILED: {TaskStatus.RECOVERY, TaskStatus.ESCALATED},
    TaskStatus.RECOVERY: {TaskStatus.RUNNING, TaskStatus.ESCALATED},
    TaskStatus.COMPLETED: set(),
    TaskStatus.ESCALATED: set(),
    TaskStatus.CANCELLED: set(),
}


class InvalidTaskTransition(ValueError):
    pass


class TaskManager:
    def __init__(self) -> None:
        self._tasks: dict[UUID, TaskRecord] = {}

    def create(self, prompt: str) -> TaskRecord:
        if not prompt.strip():
            raise ValueError("Prompt cannot be empty")
        task = TaskRecord(original_prompt=prompt)
        self._tasks[task.task_id] = task
        return task

    def get(self, task_id: UUID) -> TaskRecord:
        return self._tasks[task_id]

    def transition(self, task_id: UUID, status: TaskStatus, **changes: object) -> TaskRecord:
        current = self.get(task_id)
        if status not in _ALLOWED[current.status]:
            raise InvalidTaskTransition(f"{current.status.value} -> {status.value} is not allowed")
        updated = current.model_copy(update={
            **changes, "status": status, "updated_at": datetime.now(timezone.utc)
        })
        self._tasks[task_id] = updated
        return updated
