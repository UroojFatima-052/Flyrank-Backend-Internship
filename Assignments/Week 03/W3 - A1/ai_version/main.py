from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException, Response, status
from fastapi.responses import JSONResponse
from sqlmodel import SQLModel, Field, Session, create_engine, select
from pydantic import field_validator

app = FastAPI()


# --------------------------------------------------
# Database
# --------------------------------------------------

DATABASE_URL = "sqlite:///tasks.db"

engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False},
)


# --------------------------------------------------
# Database Model
# --------------------------------------------------

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    done: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# --------------------------------------------------
# Request Models
# --------------------------------------------------

class TaskCreate(SQLModel):
    title: str

    @field_validator("title")
    @classmethod
    def validate_title(cls, value):
        if not value.strip():
            raise ValueError("Title cannot be empty")
        return value


class TaskUpdate(SQLModel):
    title: Optional[str] = None
    done: Optional[bool] = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, value):
        if value is not None and not value.strip():
            raise ValueError("Title cannot be empty")
        return value


# --------------------------------------------------
# Error Handler
# --------------------------------------------------

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail},
    )


# Convert validation errors to HTTP 400
from fastapi.exceptions import RequestValidationError

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={"error": "Invalid request"},
    )


# --------------------------------------------------
# Startup
# --------------------------------------------------

@app.on_event("startup")
def startup():
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        count = len(session.exec(select(Task)).all())

        if count == 0:
            session.add(Task(title="Learn FastAPI"))
            session.add(Task(title="Build CRUD API", done=True))
            session.add(Task(title="Test Endpoints"))
            session.commit()


# --------------------------------------------------
# Root
# --------------------------------------------------

@app.get("/")
def root():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"],
    }


@app.get("/health")
def health():
    return {"status": "ok"}


# --------------------------------------------------
# GET ALL
# --------------------------------------------------

@app.get("/tasks")
def get_tasks():
    with Session(engine) as session:
        return session.exec(select(Task)).all()


# --------------------------------------------------
# GET ONE
# --------------------------------------------------

@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    with Session(engine) as session:
        task = session.get(Task, task_id)

        if task is None:
            raise HTTPException(
                status_code=404,
                detail=f"Task {task_id} not found",
            )

        return task


# --------------------------------------------------
# CREATE
# --------------------------------------------------

@app.post("/tasks", status_code=status.HTTP_201_CREATED)
def create_task(data: TaskCreate):
    with Session(engine) as session:
        task = Task(title=data.title)

        session.add(task)
        session.commit()
        session.refresh(task)

        return task


# --------------------------------------------------
# UPDATE
# --------------------------------------------------

@app.put("/tasks/{task_id}")
def update_task(task_id: int, update: TaskUpdate):
    if update.title is None and update.done is None:
        raise HTTPException(
            status_code=400,
            detail="Request body cannot be empty",
        )

    with Session(engine) as session:
        task = session.get(Task, task_id)

        if task is None:
            raise HTTPException(
                status_code=404,
                detail=f"Task {task_id} not found",
            )

        if update.title is not None:
            task.title = update.title

        if update.done is not None:
            task.done = update.done

        task.updated_at = datetime.utcnow()

        session.add(task)
        session.commit()
        session.refresh(task)

        return task


# --------------------------------------------------
# DELETE
# --------------------------------------------------

@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int):
    with Session(engine) as session:
        task = session.get(Task, task_id)

        if task is None:
            raise HTTPException(
                status_code=404,
                detail=f"Task {task_id} not found",
            )

        session.delete(task)
        session.commit()

        return Response(status_code=status.HTTP_204_NO_CONTENT)