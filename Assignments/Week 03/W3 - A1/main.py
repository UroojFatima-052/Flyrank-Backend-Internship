from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlmodel import Field, Session, SQLModel, create_engine, select
from contextlib import asynccontextmanager

# defining database url and engine
DATABASE_URL = "sqlite:///tasks.db"   # -------> database url
engine = create_engine(DATABASE_URL)  # -------> create the connection at that path, like a door you can use to enter a database

# A class that creates table in the database
class Task(SQLModel, table=True):   # ------> SQLModel is the base model that gives database powers to the class, otherwise it would behave as a normal python class. 
    id : int | None = Field(primary_key=True, default=None)
    title : str
    done : bool = False

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

@app.post("/tasks")
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
        
        return JSONResponse(status_code=201, content=new_task.model_dump())

#Stage 04
class TaskUpdate(BaseModel):
    title : str = None
    done : bool = None

@app.put("/tasks/{id}")
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

        session.commit()
        session.refresh(task)

        return JSONResponse(status_code=200, content=task.model_dump())

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
    with Session(engine) as session:
        all_tasks = session.exec(select(Task)).all()

    if done is None and search is None:
        return all_tasks
    
    filtered = []

    for item in all_tasks:
        done_match = (done is None) or (item.done == done)
        search_match = (search is None) or (search in item.title)
        
        if done_match and search_match:
            filtered.append(item)
            
    return filtered

# Stats
@app.get("/stats")
def stats():
    total = len(tasks)
    
    count_done = 0

    for item in tasks:
        if item["done"] is True:
            count_done += 1

    open_tasks = total - count_done

    return {"total" : total, "done" : count_done, "open" : open_tasks}

    
@app.post("/reset")
def reset():
    tasks.clear()
    
    tasks.append({"id": 1, "title": "BE-01", "done": False})
    tasks.append({"id": 2, "title": "Event Attend", "done": True})
    tasks.append({"id": 3, "title": "Exercise", "done": False})
    
    return {"message": "Tasks reset successfully"}










