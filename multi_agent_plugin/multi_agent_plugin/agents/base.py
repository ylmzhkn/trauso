"""Base interface for future model/provider adapters."""

from abc import ABC, abstractmethod
from typing import Any

from ..contracts import AgentId, TaskRecord


class Agent(ABC):
    agent_id: AgentId

    @abstractmethod
    async def handle(self, task: TaskRecord, context: dict[str, Any]) -> dict[str, Any]:
        """Handle one bounded task and return structured output."""
        raise NotImplementedError
