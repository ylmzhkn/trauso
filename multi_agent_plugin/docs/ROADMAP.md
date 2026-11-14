# Implementation roadmap

1. Core contracts, policy engine, task state machine, and local API.
2. Durable PostgreSQL repositories and migrations.
3. NATS JetStream transport, idempotency, and correlation.
4. Deterministic watchdog process and Supervisor intervention protocol.
5. Sandboxed workspace adapters and agent runtime isolation.
6. Provider adapters for Coordinator and Researcher.
7. Coder, Analyst, Verifier, Tester, and Repair tool adapters with enforced scopes.
8. Audit, telemetry, backup/restore, authentication, and operational dashboard.
9. Independent security review and explicit acceptance testing.

No tests or builds are run as part of the initial scaffold creation. Do not represent the scaffold as production-ready.
