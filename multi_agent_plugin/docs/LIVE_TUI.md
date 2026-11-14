# Live terminal task monitoring

Start the local API in one terminal:

```bash
multi-agent serve
```

Open the live dashboard in another terminal:

```bash
multi-agent tui
```

Or target a different local API:

```bash
multi-agent tui --api-url http://127.0.0.1:8787
```

The dashboard consumes Server-Sent Events from `GET /events/stream`. It displays task lifecycle events as they are emitted by the API process. The initial implementation uses an in-process event hub, so it is suitable for the current single-process local deployment. Multi-worker or distributed deployments must replace this transport with the planned NATS JetStream adapter.

The event stream is observational: it does not create, cancel, retry, or otherwise control tasks. The API currently creates queued tasks; the TUI reports only state transitions and agent activity that the runtime actually emits. It does not fabricate progress or imply that placeholder agents are executing.
