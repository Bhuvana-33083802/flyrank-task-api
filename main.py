from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(
    title="Task API",
    description=(
        "A small in-memory to-do list API. Built by hand for the FlyRank "
        "Backend internship, Week 2 Assignment A1. Data is stored in memory "
        "only and resets when the server restarts."
    ),
    version="1.0.0",
)

tasks = [
    {"id": 1, "title": "Buy milk", "done": False},
    {"id": 2, "title": "Book dentist appointment", "done": True},
    {"id": 3, "title": "Finish FlyRank Week 2 assignment", "done": False},
]

class TaskCreate(BaseModel):
    title: str | None = Field(
        default=None,
        description="The text of the task. Required, must not be blank.",
        examples=["Buy milk"],
    )

class TaskUpdate(BaseModel):
    title: str | None = Field(
        default=None,
        description="New title. Optional.",
        examples=["Buy oat milk"],
    )
    done: bool | None = Field(
        default=None,
        description="Mark complete. Optional.",
        examples=[True],
    )

def find_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            return task
    return None

@app.get("/", tags=["meta"], summary="Describe this API")
def read_root():
    """Returns the API name, version and its available endpoints."""
    return {
        "name": "Task API",
        "version": "1.0.0",
        "endpoints": ["/tasks", "/tasks/{id}"],
    }

@app.get("/health", tags=["meta"], summary="Health check")
def health():
    """Cheap liveness check used by monitoring tools."""
    return {"status": "ok"}

@app.get("/tasks", tags=["tasks"], summary="List all tasks")
def list_tasks():
    """Return every task currently in memory."""
    return tasks

@app.get(
    "/tasks/{task_id}",
    tags=["tasks"],
    summary="Get a single task",
    responses={404: {"description": "No task with that id"}},
)
def get_task(task_id: int):
    """Return one task by its id. Responds 404 if the id does not exist."""
    task = find_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return task

@app.post(
    "/tasks",
    status_code=201,
    tags=["tasks"],
    summary="Create a task",
    responses={400: {"description": "title is missing or empty"}},
)
def create_task(payload: TaskCreate):
    """Create a new task. The server assigns the id; new tasks start as not done."""
    if payload.title is None or not payload.title.strip():
        raise HTTPException(
            status_code=400,
            detail="title is required and must not be empty",
        )

    next_id = max((t["id"] for t in tasks), default=0) + 1
    new_task = {"id": next_id, "title": payload.title.strip(), "done": False}
    tasks.append(new_task)
    return new_task

@app.put(
    "/tasks/{task_id}",
    tags=["tasks"],
    summary="Update a task",
    responses={
        400: {"description": "Empty body, or an empty title"},
        404: {"description": "No task with that id"},
    },
)
def update_task(task_id: int, payload: TaskUpdate):
    """Update the title and/or done flag. Only the fields you send are changed."""
    task = find_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

    if payload.title is None and payload.done is None:
        raise HTTPException(
            status_code=400,
            detail="provide at least one field to update: title, done",
        )
    if payload.title is not None:
        if not payload.title.strip():
            raise HTTPException(status_code=400, detail="title must not be empty")
        task["title"] = payload.title.strip()
    if payload.done is not None:
        task["done"] = payload.done

    return task

@app.delete(
    "/tasks/{task_id}",
    status_code=204,
    tags=["tasks"],
    summary="Delete a task",
    responses={404: {"description": "No task with that id"}},
)
def delete_task(task_id: int):
    """Delete a task. Returns 204 with no body on success."""
    task = find_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

    tasks.remove(task)
    return None