"""Local HTTP API; remote exposure requires authentication and hardened deployment."""
import asyncio
import json
from uuid import UUID

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from .contracts import AgentId
from .events import event_hub
from .orchestrator import Orchestrator
from .task_manager import TaskManager
from .watchdog import Watchdog

app = FastAPI(title="Trauso Multi-Agent Plugin", version="0.2.0")
task_manager, watchdog = TaskManager(), Watchdog()
orchestrator = Orchestrator(task_manager, watchdog)


class TaskRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=20000)


@app.get("/health")
def health():
    return {"status": "ok", "service": "multi-agent-plugin"}


@app.get("/agents")
def agents():
    return [{"id": agent.value} for agent in AgentId]


@app.post("/tasks", status_code=202)
def create_task(request: TaskRequest):
    return orchestrator.submit(request.prompt)


@app.get("/tasks/{task_id}")
def get_task(task_id: UUID):
    try:
        return task_manager.get(task_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Task not found") from exc


@app.get("/events")
def recent_events():
    """Return the bounded in-memory event history for dashboard bootstrap."""
    return event_hub.snapshot()


@app.get("/events/stream")
async def stream_events():
    """Stream real task lifecycle events to terminal clients using SSE."""
    subscriber = event_hub.subscribe()

    async def generate():
        try:
            # Send recent state changes first, then continue with live events.
            for event in event_hub.snapshot():
                yield f"data: {json.dumps(event, default=str)}\n\n"
            while True:
                try:
                    event = await asyncio.to_thread(subscriber.get, True, 15)
                    yield f"data: {json.dumps(event, default=str)}\n\n"
                except Exception:
                    yield ": keep-alive\n\n"
        finally:
            event_hub.unsubscribe(subscriber)

    return StreamingResponse(generate(), media_type="text/event-stream", headers={
        "Cache-Control": "no-cache", "X-Accel-Buffering": "no"
    })
