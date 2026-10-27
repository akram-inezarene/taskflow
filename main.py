import os

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from pydantic import BaseModel

app = FastAPI(title="TaskFlow")
Instrumentator().instrument(app).expose(app)

VERSION = os.getenv("APP_VERSION", "dev")
tasks = []


class Task(BaseModel):
    title: str


@app.get("/")
def home():
    return {"app": "TaskFlow", "version": VERSION}


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/tasks")
def list_tasks():
    return tasks


@app.post("/api/tasks", status_code=201)
def add_task(task: Task):
    tasks.append(task.title)
    return {"id": len(tasks), "title": task.title}
