"""Deterministic liveness and loop guard; independent from LLM reasoning."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from collections import deque


@dataclass
class AgentHealth:
    last_heartbeat: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_progress: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    recent_actions: deque[str] = field(default_factory=lambda: deque(maxlen=16))


@dataclass(frozen=True)
class HealthFinding:
    healthy: bool
    reason: str | None = None
    action: str = "none"


class Watchdog:
    def __init__(self, heartbeat_timeout: int = 20, max_identical_actions: int = 3) -> None:
        self.heartbeat_timeout = heartbeat_timeout
        self.max_identical_actions = max_identical_actions
        self._agents: dict[str, AgentHealth] = {}

    def heartbeat(self, agent_id: str, *, progress: bool = False) -> None:
        now = datetime.now(timezone.utc)
        state = self._agents.setdefault(agent_id, AgentHealth())
        state.last_heartbeat = now
        if progress:
            state.last_progress = now

    def record_action(self, agent_id: str, action_fingerprint: str) -> HealthFinding:
        state = self._agents.setdefault(agent_id, AgentHealth())
        state.recent_actions.append(action_fingerprint)
        repeated = sum(item == action_fingerprint for item in state.recent_actions)
        if repeated >= self.max_identical_actions:
            return HealthFinding(False, "Repeated identical action threshold reached", "stop_and_escalate")
        return HealthFinding(True)

    def inspect(self, agent_id: str) -> HealthFinding:
        state = self._agents.get(agent_id)
        if state is None:
            return HealthFinding(False, "No heartbeat received", "restart_or_escalate")
        elapsed = (datetime.now(timezone.utc) - state.last_heartbeat).total_seconds()
        if elapsed > self.heartbeat_timeout:
            return HealthFinding(False, f"Heartbeat overdue by {elapsed:.1f}s", "stop_and_recover")
        return HealthFinding(True)
