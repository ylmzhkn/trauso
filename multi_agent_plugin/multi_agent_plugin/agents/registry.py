"""Declarative agent role registry. Runtime adapters are intentionally separate."""

from dataclasses import dataclass

from ..contracts import AgentId


@dataclass(frozen=True)
class AgentRole:
    agent_id: AgentId
    mission: str
    allowed_tools: tuple[str, ...]
    forbidden_actions: tuple[str, ...]


AGENT_ROLES: dict[AgentId, AgentRole] = {
    AgentId.SUPERVISOR: AgentRole(AgentId.SUPERVISOR, "Monitor all agent work; detect stalls, loops and failures; coordinate bounded recovery.", ("watchdog.read", "task.inspect", "task.intervene"), ("bypass_policy", "unbounded_retry")),
    AgentId.COORDINATOR: AgentRole(AgentId.COORDINATOR, "Interpret the user request, decompose it, assign subtasks and aggregate results.", ("task.create", "task.assign", "message.send"), ("internet", "filesystem", "code_execution")),
    AgentId.RESEARCHER: AgentRole(AgentId.RESEARCHER, "Perform scoped internet research and share cited findings with dependent agents.", ("web.search", "web.open", "message.send"), ("workspace_filesystem", "file_write")),
    AgentId.ANALYST: AgentRole(AgentId.ANALYST, "Inspect local workspace files and report findings without modifying them.", ("workspace.read", "static_analysis"), ("internet", "file_write", "terminal")),
    AgentId.CODER: AgentRole(AgentId.CODER, "Implement only the assigned change within the authorized workspace scope.", ("workspace.read", "workspace.write", "message.send"), ("internet", "test", "build", "runtime_execution", "independent_file_discovery")),
    AgentId.VERIFIER: AgentRole(AgentId.VERIFIER, "Independently inspect changed source against the immutable original user request.", ("workspace.read", "static_review"), ("internet", "terminal", "test", "build", "agent_reports_as_evidence", "file_write")),
    AgentId.TESTER: AgentRole(AgentId.TESTER, "Run only explicitly authorized tests within the approved scope.", ("test.run_if_authorized",), ("implicit_test", "unapproved_build_or_execution")),
    AgentId.REPAIR: AgentRole(AgentId.REPAIR, "Repair a concrete reported defect, changing only demonstrably affected files.", ("workspace.read", "workspace.write_scoped"), ("speculative_changes", "unrelated_refactor")),
}


def get_agent_role(agent_id: AgentId) -> AgentRole:
    return AGENT_ROLES[agent_id]
