# Multi-Agent Plugin

Independent eight-agent plugin scaffold. It does not implement or modify Trauso's TeraBox download workflow.

## Included in this scaffold
- Eight role definitions and separate agent classes.
- Typed task/message contracts and task lifecycle state machine.
- Default-deny capability policy and explicit test-authorization gate.
- Deterministic heartbeat and repeated-action watchdog primitives.
- Local FastAPI health, agent-list, task-submission, and Server-Sent Events endpoints.
- Textual terminal dashboard for live task/event monitoring.
- Docker configuration for API, PostgreSQL, and NATS.

## Not yet production-ready
LLM/provider adapters, durable PostgreSQL repository, NATS JetStream transport, OS-level agent isolation, sandboxed filesystem adapters, real web research, authentication, secrets management, observability, and dashboard remain to be implemented. The current API stores tasks in memory.

## Local development
Requires Python 3.12+.

```bash
cd multi_agent_plugin
python -m venv .venv
pip install -e .
multi-agent serve
# In a second terminal:
multi-agent tui
```

Endpoints: `GET /health`, `GET /agents`, `POST /tasks`, `GET /tasks/{task_id}`, `GET /events`, and live `GET /events/stream`.

See [Live TUI guide](docs/LIVE_TUI.md). The current event hub is in-process and intended for the single-process local MVP; distributed deployments require the NATS transport. The TUI displays only events actually emitted by the runtime. Since agent execution/provider adapters are not yet implemented, it does not yet show fabricated per-agent reasoning or progress.

## Local infrastructure
Copy `.env.example` to `.env`, review credentials, then run:

```bash
docker compose -f infrastructure/docker-compose.yml up --build
```

Example credentials are for local development only. Ports bind to loopback.

## Safety invariants
- Testing is disabled unless system configuration and explicit per-task approval are both present.
- Coordinator has no filesystem or internet capability.
- Researcher is the only role granted web research.
- Analyst and Verifier are read-only.
- Coder cannot research or execute tests/builds.
- Repair requires a concrete error and scoped affected-file list.
- Runtime adapters must enforce policy outside model prompts.
