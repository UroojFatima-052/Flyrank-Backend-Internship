from typing import Optional

from fastapi import FastAPI, HTTPException, Response, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator

app = FastAPI()


# -------------------------
# In-memory database
# -------------------------

tasks = [
    {"id": 1, "title": "Learn FastAPI", "done": False},
    {"id": 2, "title": "Build CRUD API", "done": True},
    {"id": 3, "title": "Test endpoints", "done": False},
]


# -------------------------
# Models
# -------------------------

class TaskCreate(BaseModel):
    title: str = Field(...)

    @field_validator("title")
    @classmethod
    def validate_title(cls, value):
        if value.strip() == "":
            raise ValueError("Title cannot be empty")
        return value


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, value):
        if value is not None and value.strip() == "":
            raise ValueError("Title cannot be empty")
        return value


# -------------------------
# Custom Error Handler
# -------------------------

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )


# -------------------------
# Stage 0
# -------------------------

@app.get("/hello")
def hello():
    return {"message": "Hello from FastAPI!"}


# -------------------------
# Stage 1
# -------------------------

@app.get("/")
def root():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"]
    }


@app.get("/health")
def health():
    return {"status": "ok"}


# -------------------------
# Stage 2
# -------------------------

@app.get("/tasks")
def get_tasks():
    return tasks


@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            return task

    raise HTTPException(
        status_code=404,
        detail=f"Task {task_id} not found"
    )


# -------------------------
# Stage 3
# -------------------------

@app.post("/tasks", status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate):
    new_id = max((t["id"] for t in tasks), default=0) + 1

    new_task = {
        "id": new_id,
        "title": task.title,
        "done": False
    }

    tasks.append(new_task)

    return new_task


# -------------------------
# Stage 4
# -------------------------

@app.put("/tasks/{task_id}")
def update_task(task_id: int, update: TaskUpdate):

    if update.title is None and update.done is None:
        raise HTTPException(
            status_code=400,
            detail="Request body cannot be empty"
        )

    for task in tasks:
        if task["id"] == task_id:

            if update.title is not None:
                task["title"] = update.title

            if update.done is not None:
                task["done"] = update.done

            return task

    raise HTTPException(
        status_code=404,
        detail=f"Task {task_id} not found"
    )


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int):

    for index, task in enumerate(tasks):
        if task["id"] == task_id:
            tasks.pop(index)
            return Response(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(
        status_code=404,
        detail=f"Task {task_id} not found"
    )