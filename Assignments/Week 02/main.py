from fastapi import FastAPI, HTTPException

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

@app.get("/")
def home():
    return { "name": "Task API", "version": "1.0", "endpoints": ["/tasks"] }

@app.get("/health")
def status():
    return {"status" : "ok"}

@app.get("/tasks")
def all_tasks():
    return tasks

@app.get("/tasks/{id}")
def specific_tasks(id : int):
    for item in tasks:
        if item["id"] == id:
            return item
        
    raise HTTPException(status_code=404, detail=f"Task {id} not found")
