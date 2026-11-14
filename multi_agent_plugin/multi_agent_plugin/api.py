"""Local HTTP API; remote exposure requires authentication and hardened deployment."""
from uuid import UUID
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from .contracts import AgentId
from .orchestrator import Orchestrator
from .task_manager import TaskManager
from .watchdog import Watchdog

app = FastAPI(title="Trauso Multi-Agent Plugin", version="0.1.0")
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
