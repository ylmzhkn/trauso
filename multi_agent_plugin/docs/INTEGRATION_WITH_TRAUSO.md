# Trauso integration boundary

The multi-agent system is an independent subsystem. Do not import it into or alter the TeraBox downloader business logic.

## Proposed integration
1. Run the plugin as a local sidecar service on loopback.
2. Expose a narrow, versioned HTTP interface to the desktop shell.
3. Keep task state, agent runtimes, policy enforcement, and audit records inside the plugin boundary.
4. Require explicit user interaction before privileged operations such as test execution.
5. Do not share Trauso download credentials, cookies, or private state with agent prompts.

## Current state
Only the local API scaffold exists. No Tauri command, frontend panel, automatic startup hook, or IPC bridge has been added. Integration should follow implementation of authentication and policy enforcement.
