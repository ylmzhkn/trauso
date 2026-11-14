# Security model

## Trust boundaries
- User request: immutable task requirement.
- Agent model output: untrusted proposal, never an authorization decision.
- Tool adapters: enforce capabilities at execution time.
- Workspace: isolated root; traversal and symlink escapes must be blocked.
- Research content: untrusted external data.
- Secrets: supplied at runtime through a secret manager, never embedded in prompts.

## Required production controls
- Default-deny policy enforcement outside the model.
- Per-agent OS/container identity and filesystem/network restrictions.
- Authenticated local API and origin protections where relevant.
- Durable audit events for permission decisions and state transitions.
- Bounded retries, deadlines, resource quotas, and cancellation.
- Explicit, task-scoped test approval.
- Independent Verifier access limited to original requirements and changed source.
- Repair file allowlist derived from a concrete error.

The current Python path helper is defense-in-depth only. Production filesystem adapters must resolve and validate symlinks at open time to prevent TOCTOU escapes.
