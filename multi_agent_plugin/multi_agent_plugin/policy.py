"""Default-deny policy enforcement for agent capabilities."""

from dataclasses import dataclass
from enum import StrEnum

from .contracts import AgentId


class Capability(StrEnum):
    ORCHESTRATE = "orchestrate"
    WEB_RESEARCH = "web_research"
    WORKSPACE_READ = "workspace_read"
    WORKSPACE_WRITE = "workspace_write"
    TEST_EXECUTION = "test_execution"
    SUPERVISE = "supervise"
    REPAIR = "repair"


@dataclass(frozen=True)
class AgentPolicy:
    capabilities: frozenset[Capability]
    workspace_read_only: bool = True


POLICIES: dict[AgentId, AgentPolicy] = {
    AgentId.SUPERVISOR: AgentPolicy(frozenset({Capability.SUPERVISE})),
    AgentId.COORDINATOR: AgentPolicy(frozenset({Capability.ORCHESTRATE})),
    AgentId.RESEARCHER: AgentPolicy(frozenset({Capability.WEB_RESEARCH})),
    AgentId.ANALYST: AgentPolicy(frozenset({Capability.WORKSPACE_READ})),
    AgentId.CODER: AgentPolicy(frozenset({Capability.WORKSPACE_READ, Capability.WORKSPACE_WRITE}), False),
    AgentId.VERIFIER: AgentPolicy(frozenset({Capability.WORKSPACE_READ})),
    AgentId.TESTER: AgentPolicy(frozenset({Capability.TEST_EXECUTION})),
    AgentId.REPAIR: AgentPolicy(frozenset({Capability.WORKSPACE_READ, Capability.WORKSPACE_WRITE}), False),
}


class PolicyDenied(PermissionError):
    """Raised when an agent attempts an ungranted capability."""


class PolicyEngine:
    def __init__(self, test_execution_enabled: bool = False) -> None:
        self._test_execution_enabled = test_execution_enabled

    def authorize(self, agent: AgentId, capability: Capability, *, user_approved: bool = False) -> None:
        policy = POLICIES[agent]
        if capability not in policy.capabilities:
            raise PolicyDenied(f"{agent.value} is not allowed to use {capability.value}")
        if capability == Capability.TEST_EXECUTION:
            if not self._test_execution_enabled or not user_approved:
                raise PolicyDenied("Testing requires system enablement and explicit user approval")

    def can_access_workspace_path(self, agent: AgentId, path: str, workspace_root: str) -> bool:
        """Lexically constrain paths. Production adapters must additionally resolve symlinks safely."""
        from pathlib import Path

        root = Path(workspace_root).resolve()
        candidate = (root / path).resolve()
        try:
            candidate.relative_to(root)
        except ValueError:
            return False
        return Capability.WORKSPACE_READ in POLICIES[agent].capabilities or (
            Capability.WORKSPACE_WRITE in POLICIES[agent].capabilities
        )
