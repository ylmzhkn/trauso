"""Live terminal dashboard for task and agent events."""
from __future__ import annotations

import json
from datetime import datetime
from typing import Any

import httpx
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import DataTable, Footer, Header, Static


class LiveTaskApp(App[None]):
    TITLE = "Trauso Multi-Agent • Live Monitor"
    CSS = """
    Screen { layout: vertical; }
    #summary { height: 3; padding: 1; background: $panel; }
    #events { height: 1fr; }
    #tasks { height: 12; }
    """

    def __init__(self, api_url: str = "http://127.0.0.1:8787") -> None:
        super().__init__()
        self.api_url = api_url.rstrip("/")
        self.event_count = 0
        self.latest: dict[str, dict[str, Any]] = {}

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("Connecting to local task event stream…", id="summary")
        with Vertical():
            yield DataTable(id="tasks")
            yield DataTable(id="events")
        yield Footer()

    def on_mount(self) -> None:
        tasks = self.query_one("#tasks", DataTable)
        tasks.add_columns("Task ID", "Status", "Agent", "Updated")
        events = self.query_one("#events", DataTable)
        events.add_columns("Time", "Event", "Task", "Details")
        self.run_worker(self._listen(), name="event-stream", exclusive=True)

    async def _listen(self) -> None:
        summary = self.query_one("#summary", Static)
        try:
            async with httpx.AsyncClient(timeout=None) as client:
                async with client.stream("GET", f"{self.api_url}/events/stream") as response:
                    response.raise_for_status()
                    summary.update(f"LIVE  •  {self.api_url}  •  connected")
                    async for line in response.aiter_lines():
                        if not line.startswith("data:"):
                            continue
                        try:
                            event = json.loads(line[5:].strip())
                        except json.JSONDecodeError:
                            continue
                        self._render_event(event)
        except Exception as exc:
            summary.update(f"DISCONNECTED  •  {exc}  •  API: {self.api_url}")

    def _render_event(self, event: dict[str, Any]) -> None:
        self.event_count += 1
        task_id = str(event.get("task_id") or "—")
        data = event.get("data") or {}
        timestamp = str(event.get("timestamp") or "")
        short_time = timestamp[11:19] if len(timestamp) >= 19 else timestamp
        event_type = str(event.get("type", "event"))
        details = json.dumps(data, ensure_ascii=False, default=str)
        events = self.query_one("#events", DataTable)
        events.add_row(short_time, event_type, task_id[:8], details[:180])
        if events.row_count > 250:
            events.remove_row(next(iter(events.rows)))

        if event_type in {"task.created", "task.status_changed"}:
            current = self.latest.setdefault(task_id, {})
            current.update(data)
            current["task_id"] = task_id
            tasks = self.query_one("#tasks", DataTable)
            # Rebuild the compact table to keep rows consistent without stale state.
            tasks.clear()
            for item in self.latest.values():
                tasks.add_row(
                    item.get("task_id", "")[:8],
                    str(item.get("status", "created")),
                    str(item.get("assigned_agent") or "—"),
                    str(item.get("updated_at") or "")[-14:],
                )
        self.query_one("#summary", Static).update(
            f"LIVE  •  events: {self.event_count}  •  tracked tasks: {len(self.latest)}  •  Ctrl+C to exit"
        )


def run_tui(api_url: str = "http://127.0.0.1:8787") -> None:
    LiveTaskApp(api_url).run()
