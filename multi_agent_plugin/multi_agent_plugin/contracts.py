"""Shared, versionable contracts for tasks and agent messages."""

from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class AgentId(StrEnum):
    SUPERVISOR = "supervisor"
    COORDINATOR = "coordinator"
    RESEARCHER = "researcher"
    ANALYST = "analyst"
    CODER = "coder"
    VERIFIER = "verifier"
    TESTER = "tester"
    REPAIR = "repair"


class TaskStatus(StrEnum):
    CREATED = "created"
    QUEUED = "queued"
    ASSIGNED = "assigned"
    RUNNING = "running"
    WAITING = "waiting"
    COMPLETED = "completed"
    FAILED = "failed"
    RECOVERY = "recovery"
    ESCALATED = "escalated"
    CANCELLED = "cancelled"


class MessageType(StrEnum):
    TASK_REQUEST = "TASK_REQUEST"
    TASK_ACCEPTED = "TASK_ACCEPTED"
    TASK_PROGRESS = "TASK_PROGRESS"
    TASK_RESULT = "TASK_RESULT"
    ERROR_EVENT = "ERROR_EVENT"
    REPAIR_REQUEST = "REPAIR_REQUEST"
    VALIDATION_RESULT = "VALIDATION_RESULT"
    TEST_RESULT = "TEST_RESULT"
    AGENT_HEARTBEAT = "AGENT_HEARTBEAT"
    AGENT_STOP = "AGENT_STOP"


class AgentMessage(BaseModel):
    model_config = ConfigDict(frozen=True)
    schema_version: str = "1.0"
    message_id: UUID = Field(default_factory=uuid4)
    task_id: UUID
    sender: AgentId
    recipient: AgentId
    message_type: MessageType
    priority: str = "normal"
    payload: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utc_now)
    correlation_id: UUID = Field(default_factory=uuid4)


class TaskRecord(BaseModel):
    task_id: UUID = Field(default_factory=uuid4)
    original_prompt: str
    status: TaskStatus = TaskStatus.CREATED
    assigned_agent: AgentId | None = None
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    retry_count: int = 0
    checkpoint: dict[str, Any] = Field(default_factory=dict)
    result: dict[str, Any] | None = None
    error: str | None = None
