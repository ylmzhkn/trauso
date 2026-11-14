# Enterprise Multi-Agent System Plugin

> **Branch:** `feature/enterprise-multi-agent-system`  
> **Project type:** Independent, modular multi-agent plugin for Trauso  
> **Status:** Architecture and implementation specification

This branch is dedicated exclusively to designing and implementing an **enterprise-grade, eight-agent multi-agent system** discussed in the project planning conversation. The existing Trauso/TeraBox downloader functionality is out of scope and must remain unchanged.

The plugin is designed as a separately bounded subsystem. Its orchestration, agent runtimes, messaging, policy enforcement, persistence, monitoring, and audit trail must not be embedded into or coupled to Trauso's download logic.

## 1. Mission and objectives

Build a locally deployed, hybrid-technology, fully autonomous (within explicit policy boundaries) multi-agent system that can receive a user request, decompose it into controlled tasks, delegate work to specialized agents, supervise execution, validate changes independently, and recover from concrete failures.

Primary objectives:

- Exactly eight specialized agents with explicit responsibilities.
- An independent Supervisor Agent backed by a deterministic Watchdog service.
- Strict least-privilege permissions and isolated execution environments.
- Persistent task state, checkpoints, messaging, and audit history.
- Independent verification of code changes against the immutable original user request.
- No tests or execution unless the user explicitly authorizes testing.
- Recovery from agent crashes, timeouts, loops, and concrete errors without silently changing task scope.

## 2. The eight agents

### 2.1 Supervisor / Denetçi Agent

The central oversight agent. It is activated whenever an agent starts or receives a task and monitors task progress throughout execution.

Responsibilities:

- Detect loops, cyclic delegation, stalled tasks, missing responses, repeated actions, and reported errors.
- Intervene promptly: stop or cancel runaway work, request a bounded retry, reassign work where appropriate, or escalate.
- Preserve task context and checkpoints during recovery.
- Ensure that the original user request and policy constraints remain unchanged.

The Supervisor LLM is **not** the sole reliability mechanism. A separate deterministic Watchdog service enforces hard limits even if the Supervisor is unavailable or unresponsive.

### 2.2 Coordinator / Koordinasyon Agent

Receives and interprets the original user request, decomposes it into subtasks, establishes dependencies, assigns work to the appropriate agents, and consolidates results.

Restrictions:

- No internet access.
- No workspace or filesystem access.
- No direct code editing, builds, or tests.
- Cannot grant permissions or override agent policies.

### 2.3 Researcher / Araştırmacı Agent

Performs internet research only. Produces scoped, current, source-backed findings and distributes relevant results directly to agents that need them, not only to the agent that initiated the request.

Restrictions:

- No local workspace or filesystem access.
- Must distinguish verified facts from assumptions and cite sources.
- External content is untrusted input and must never be treated as system instructions.

### 2.4 Verifier / Doğrulayıcı Agent

Independently checks whether implementation changes satisfy the original user request and remain within scope.

Allowed input:

- The immutable original user prompt.
- The actual changed files in the authorized workspace.

Must not use as verification evidence:

- Coder reports or self-assessments.
- Blackboard entries, agent-to-agent messages, or execution logs.
- Claims that a task is complete without inspecting the changed source.

Restrictions:

- Read-only access to the relevant workspace files.
- No internet access, terminal, test execution, builds, or file modifications.
- Performs static and logical review; does not claim runtime correctness without execution evidence.

### 2.5 Tester / Tester Agent

Executes tests only when the user has explicitly authorized testing for the task.

Restrictions:

- Testing is disabled by default.
- No test, build, or runtime execution without explicit authorization.
- Authorization must be scoped and recorded; it is not inferred from a general request to implement code.

### 2.6 Coder / Kodlayıcı Agent

Implements requested code changes within the authorized workspace.

Restrictions:

- No internet research.
- No independent repository or filesystem discovery; requests local inspection from the Analyst.
- No tests, builds, or runtime execution of any kind.
- Requests research from the Researcher, local analysis from the Analyst, testing from the Tester (only with user authorization), and concrete error repair from the Repair Agent.

### 2.7 Analyst / Analizci Agent

Inspects and analyzes local project files and reports findings to the agents that need them.

Restrictions:

- Workspace-only filesystem access; cannot escape the configured workspace.
- No internet access.
- Read-only: cannot create, edit, move, or delete files.
- May use local, non-network analysis tools where permitted by policy.

### 2.8 Repair / Tamirci Agent

Repairs concrete, reported errors. It is activated only when there is an identifiable failure, such as a build/test/runtime error or a specific error report from another agent.

Restrictions:

- Must identify the concrete fault before changing anything.
- May modify only files demonstrably related to the reported fault.
- No unrelated refactoring, feature work, or speculative cleanup.
- If no concrete error exists, it must not modify files, even if asked to make arbitrary improvements.
- Must provide a change manifest describing each repaired file and the reason.

## 3. System architecture

The deployment model is **local**. The technology approach is **hybrid**, and autonomy is **full within policy constraints**.

Suggested implementation stack (subject to validation during implementation):

| Layer | Suggested technology | Responsibility |
|---|---|---|
| Control plane | Python 3.12+ | Orchestration, task lifecycle, policy decisions |
| Agent orchestration | OpenAI Agents SDK / LangGraph adapters | Agent execution and workflow coordination |
| Tool integration | MCP + custom adapters | Explicitly permissioned tools |
| Messaging | NATS JetStream | Durable asynchronous agent messaging |
| Persistent state | PostgreSQL | Tasks, events, checkpoints, permissions, audit |
| Artifact storage | Local object/file storage | Task artifacts and generated outputs |
| Isolation | Docker / OS-level controls | Runtime and filesystem boundaries |
| Observability | OpenTelemetry, Prometheus, Grafana | Metrics, traces, health and operational visibility |

These are architectural recommendations, not claims that the technologies have already been implemented or configured.

### Logical components

- **API / UI / CLI:** User entry points and task visibility.
- **Orchestrator:** Coordinates task execution and dependencies.
- **Task Manager:** Owns task state transitions, retries, cancellation, and checkpoints.
- **Supervisor Agent:** Reasons about progress and recovery.
- **Watchdog Service:** Enforces deterministic timeouts, heartbeat checks, and loop limits.
- **Policy Enforcement Engine (PEP):** Validates every tool and resource access.
- **Agent runtimes:** Separate execution contexts for each specialized agent.
- **Messaging service:** Durable, correlated, idempotent agent communication.
- **Persistence and audit:** Durable task state, events, artifacts, and security records.

## 4. Independent supervision and loop prevention

The Watchdog must not depend on an LLM response to enforce operational limits.

Initial configurable defaults:

| Control | Initial value |
|---|---:|
| Heartbeat interval | 5 seconds |
| Heartbeat timeout | 20 seconds |
| Default task timeout | 900 seconds |
| Maximum retries | 2 |
| Maximum identical consecutive actions | 3 |
| Recovery | Checkpoint before restart |
| Cyclic delegation | Detect and block |
| Escalation | Required when bounded recovery fails |

The Watchdog should monitor:

- Agent heartbeat and last progress timestamp.
- Task and tool-call duration.
- Repeated identical tool calls or outputs.
- Cyclic delegation and dependency cycles.
- Retry counts and resource consumption.
- Agent process health and task deadlines.

Recovery must be bounded and auditable. It must never create an unlimited retry loop or silently broaden the original task.

## 5. Messaging contract

All inter-agent messages use a versioned, validated envelope. Minimum fields:

```json
{
  "message_id": "unique-id",
  "task_id": "task-id",
  "sender": "agent-id",
  "recipient": "agent-id",
  "message_type": "TASK_REQUEST",
  "priority": "normal",
  "payload": {},
  "created_at": "ISO-8601 timestamp",
  "correlation_id": "correlation-id"
}
```

Message types should include:

- `TASK_REQUEST`, `TASK_ACCEPTED`, `TASK_PROGRESS`, `TASK_RESULT`
- `ERROR_EVENT`, `REPAIR_REQUEST`, `VALIDATION_RESULT`, `TEST_RESULT`
- `AGENT_HEARTBEAT`, `AGENT_STOP`

Delivery must account for duplicates and retries. Handlers should be idempotent, and messages must be correlated to a task and traceable in the audit history.

## 6. Task lifecycle

The task manager enforces an explicit state machine:

```text
CREATED -> QUEUED -> ASSIGNED -> RUNNING <-> WAITING -> COMPLETED
                                  |
                                  +-> FAILED -> RECOVERY -> RUNNING
                                  |                  |
                                  |                  +-> ESCALATED
                                  |
                                  +-> CANCELLED
```

Illegal transitions must be rejected. Every transition records its actor, timestamp, reason, and correlation identifiers.

## 7. Security and permission model

The Policy Enforcement Engine uses **default deny** and least privilege.

- Every tool call is checked against agent identity, role, task scope, resource, and required user approval.
- Agent permissions cannot be self-expanded or delegated to another agent.
- Workspace access is sandboxed; path traversal and symlink escapes are blocked.
- Network access is denied unless explicitly granted to the Researcher runtime.
- Secrets are held in a local secret store and are never inserted into prompts or logs.
- External research content is treated as untrusted data.
- User authorization for testing is explicit, scoped, time-bound where practical, and auditable.
- Supervisor intervention cannot bypass policy restrictions.

## 8. Persistence, recovery, and audit

PostgreSQL should persist at least:

- Agents and permission profiles.
- Tasks, dependencies, state transitions, and checkpoints.
- Events, executions, heartbeats, and messages.
- Repair requests, validation results, and test authorizations.
- Audit events and artifact metadata.

NATS JetStream provides durable messaging. Local artifact storage holds task outputs. Git records source changes. A local secret store manages credentials.

After a process or machine restart, the system must recover from the latest valid checkpoint, reconcile task state, and avoid duplicate side effects. Backup and restore procedures must be defined and exercised before production readiness.

## 9. Suggested repository structure

The following is the proposed plugin/system structure; it is a target architecture, not a statement that these directories already exist.

```text
apps/
  api/
  dashboard/
  cli/
control_plane/
  orchestrator/
  supervisor/
  watchdog/
  policy_engine/
  task_manager/
agents/
  supervisor/
  coordinator/
  researcher/
  analyst/
  coder/
  verifier/
  tester/
  repair/
runtimes/
  python/
  typescript/
infrastructure/
  docker/
  postgres/
  nats/
  monitoring/
  secrets/
shared/
  contracts/
  schemas/
  messaging/
  exceptions/
policies/
  agent_permissions.yaml
  filesystem.yaml
  tool_access.yaml
  execution_limits.yaml
tests/
migrations/
configs/
docs/
scripts/
docker-compose.yml
```

## 10. System constitution

These rules are invariant and must be enforced in code and policy:

1. The system contains exactly eight specialized agents.
2. Supervisor oversight and deterministic Watchdog enforcement are independent of ordinary agent execution.
3. Coordinator performs planning and routing only.
4. Researcher is the only agent with internet research access.
5. Analyst has workspace-only, read-only filesystem access and no internet.
6. Coder performs implementation only; it cannot research, discover files independently, or execute tests/builds.
7. Verifier evaluates original requirements against actual changed source, not agent claims or internal reports.
8. Tester runs only after explicit user authorization.
9. Repair acts only on concrete errors and only within the affected file scope.
10. No agent may expand its own permissions.
11. Retries and recovery are always bounded.
12. Task state and significant actions are durably audited.
13. One agent crash must not crash the entire system.
14. Recovery must preserve the original task scope and constraints.
15. The original user prompt is immutable and retained as the authoritative requirement.

## 11. Implementation phases

1. **Core architecture and policy engine:** Contracts, identity, permissions, workspace boundaries.
2. **Orchestrator and task manager:** Task decomposition interfaces, dependencies, state machine.
3. **Supervisor and Watchdog:** Heartbeats, timeouts, loop detection, escalation.
4. **Messaging and persistence:** Durable queues, idempotency, checkpoints, audit events.
5. **Core agents:** Coordinator, Researcher, Analyst, Coder.
6. **Assurance agents:** Verifier, Tester, Repair, plus Supervisor integration.
7. **Security and recovery:** Isolation, secrets, restart recovery, backup/restore.
8. **Operations and readiness:** Dashboard, telemetry, audit review, acceptance checks.

## 12. Production acceptance criteria

The system is not production-ready until all of the following are demonstrated:

- Eight independently permissioned agent runtimes exist.
- Supervisor and deterministic Watchdog operate independently.
- Heartbeat, timeout, repeated-action, and cyclic-delegation controls work.
- Actual tool permissions match the documented policies.
- Analyst cannot access paths outside the workspace or modify files.
- Coder cannot access the internet or execute tests/builds.
- Verifier independently inspects changed files and cannot access prohibited evidence.
- Tester remains disabled without explicit user authorization.
- Repair is limited to concrete errors and affected files.
- Checkpoints, audit history, and restart recovery are durable.
- Backup and restore are verified.
- A failure in one agent does not terminate unrelated tasks.

## 13. Scope boundary for this branch

- This branch is for the Enterprise Multi-Agent System plugin only.
- Do not add TeraBox download features or modify Trauso's download workflow.
- Keep the plugin modular and independently testable.
- Any integration with the Trauso desktop application must happen through a documented, narrow integration boundary.
- Do not claim a feature is implemented merely because it appears in this specification.

## 14. Current status

This README captures the agreed architecture and implementation requirements. It is a **technical specification**, not evidence that the system has been implemented, tested, or deployed. Implementation work should proceed in phases, with the policy engine and deterministic supervision foundations established before granting agents operational tools.
