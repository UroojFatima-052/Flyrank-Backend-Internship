from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI()

tasks = [
    {
        "id" : 1,
        "title" : "BE-01",
        "done" : False
    },

    {
        "id" : 2,
        "title" : "Event Attend",
        "done" : True

    },

    {
        "id" : 3,
        "title" : "Exercise",
        "done" : False
    }
]

# Stage 01
@app.get("/")
def home():
    return { "name": "Task API", "version": "1.0", "endpoints": ["/tasks"] }

@app.get("/health")
def status():
    return {"status" : "ok"}

# Stage 02
@app.get("/tasks")
def all_tasks():
    return tasks

@app.get("/tasks/{id}")
def specific_tasks(id : int):
    for item in tasks:
        if item["id"] == id:
            return item
        
    raise HTTPException(status_code=404, detail=f"Task {id} not found")


# Stage 03
class TaskInput(BaseModel):
    title : str

@app.post("/tasks")
async def add_tasks(task: TaskInput):
    if not task.title or task.title.strip() == "":
        return JSONResponse(status_code=400, content={"error": "Title cannot be empty"})

    new_task = {
        "id" : len(tasks) + 1,
        "title" : task.title,
        "done" : False 
        }
    
    tasks.append(new_task)
    return JSONResponse(status_code=201, content=new_task)

#Stage 04
class TaskUpdate(BaseModel):
    title : str = None
    done : bool = None

@app.put("/tasks/{id}")
def update_tasks(id : int, task : TaskUpdate):
    if task.title is None and task.done is None:
        return JSONResponse(status_code=400, content={"error": "Data cannot be empty"})
    
    for item in tasks:
        if item["id"] == id:
            if task.title is not None:
                item['title'] = task.title
            if task.done is not None:
                item['done'] = task.done

            return JSONResponse(status_code=200, content=item)
    
    raise HTTPException(status_code=404, detail=f"Task {id} not found")


@app.delete("/tasks/{id}")
def delete_tasks(id : int):
    for item in tasks:
        if item["id"] == id:
            tasks.remove(item)
            return Response(status_code=204)
        
    raise HTTPException(status_code=404, detail=f"Task {id} not found")
    
    
    








