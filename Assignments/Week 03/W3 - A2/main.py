from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlmodel import Field, Session, SQLModel, create_engine, select
from contextlib import asynccontextmanager
from datetime import datetime

# defining database url and engine
DATABASE_URL = "sqlite:///tasks.db"   # -------> database url
engine = create_engine(DATABASE_URL)  # -------> create the connection at that path, like a door you can use to enter a database

# A class that creates table in the database
class Task(SQLModel, table=True):   # ------> SQLModel is the base model that gives database powers to the class, otherwise it would behave as a normal python class. 
    id : int | None = Field(primary_key=True, default=None)
    title : str
    done : bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# database function
def create_db():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        existing = session.exec(select(Task)).all()
        if not existing:
            tasks = [
                Task(title="BE-01", done=False),
                Task(title="Event Attend", done=True),
                Task(title="Exercise", done=False),
            ]
            for task in tasks:
                session.add(task)
  
            session.commit()

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db()
    yield

app = FastAPI(lifespan=lifespan)


# Stage 01
@app.get("/")
def home():
    return { "name": "Task API", "version": "1.0", "endpoints": ["/tasks"] }

@app.get("/health")
def status():
    return {"status" : "ok"}

# # Stage 02  --------> committed because extras query parameter part covers "all tasks" case
# @app.get("/tasks")
# def all_tasks():
#     return tasks

@app.get("/tasks/{id}")
def specific_tasks(id : int):
    with Session(engine) as session:
        all_tasks = session.exec(select(Task)).all()

    for item in all_tasks:
        if item.id == id:
            return item
        
    raise HTTPException(status_code=404, detail=f"Task {id} not found")

# Stage 03
class TaskInput(BaseModel):
    title : str

@app.post("/tasks", status_code=201)
async def add_tasks(task: TaskInput):
    if not task.title or task.title.strip() == "":
        return JSONResponse(status_code=400, content={"error": "Title cannot be empty"})
    
    new_task = Task(
        title = task.title,
        done = False )
    
    with Session(engine) as session:
        session.add(new_task)
        session.commit()
        session.refresh(new_task)
        
        return new_task

#Stage 04
class TaskUpdate(BaseModel):
    title : str = None
    done : bool = None

@app.put("/tasks/{id}", status_code=200)
def update_tasks(id : int, user_task : TaskUpdate):
    if user_task.title is None and user_task.done is None:
        return JSONResponse(status_code=400, content={"error": "Data cannot be empty"})
    
    with Session(engine) as session:
        task = session.get(Task, id)

        if task is None:
            raise HTTPException(status_code=404, detail=f"Task {id} not found")
        
        if user_task.title is not None:
            task.title = user_task.title
        if user_task.done is not None:
            task.done = user_task.done

        task.updated_at = datetime.utcnow()

        session.commit()
        session.refresh(task)

        return task

@app.delete("/tasks/{id}")
def delete_tasks(id : int):
    with Session(engine) as session:
        task = session.get(Task, id)

        if task is None:
            raise HTTPException(status_code=404, detail=f"Task {id} not found")

        session.delete(task)
        session.commit()
        return Response(status_code=204)
    
    
# Extras
# Query Parameter & Search Parameter
@app.get("/tasks")
def parameterized_tasks(done: bool = None, search: str = None):
    query = select(Task)

    if done is not None:
        query = query.where(Task.done == done)

    if search is not None:
        query = query.where(Task.title.contains((search)))

    query = query.order_by(Task.title)

    with Session(engine) as session:
        return session.exec(query).all()

# Stats
@app.get("/stats")
def stats():
    with Session(engine) as session:
        all_tasks = session.exec(select(Task)).all()

    total = len(all_tasks)
    
    count_done = 0

    for item in all_tasks:
        if item.done is True:
            count_done += 1

    open_tasks = total - count_done

    return {"total" : total, "done" : count_done, "open" : open_tasks}

    











