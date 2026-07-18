# W2 - A1: Build Your First CRUD API

## What is this

A Task Manager API built with FastAPI and Python. Manages a to-do list with full CRUD — create, read, update, and delete tasks. Data lives in memory, which means it disappears on restart. That's not a bug, that's the whole point of next week.

## How to Run

```bash
pip install fastapi uvicorn
uvicorn main:app --reload
```

## Endpoints

```
GET    /              - API info
GET    /health        - Health check  
GET    /tasks         - Get all tasks
GET    /tasks/{id}    - Get one task by ID
POST   /tasks         - Create a new task
PUT    /tasks/{id}    - Update title or done status
DELETE /tasks/{id}    - Remove a task
```

## Status Codes

```
200 - Got it
201 - Created it
204 - Deleted it, nothing to say
400 - Your request is broken
404 - That doesn't exist here
```

## curl Example

```bash
curl -i -X POST http://localhost:8000/tasks -H "Content-Type: application/json" -d '{"title":"Buy milk"}'
```

```
HTTP/1.1 201 Created
{"id":4,"title":"Buy milk","done":false}
```

## Swagger UI

```
Open http://localhost:8000/docs to test all endpoints visually.
```

![alt text](swagger.png)

## AI vs Me

**My prompt:**
I need your help building a CRUD API. I have chosen Python with FastAPI for this task.

Stage 0: Set up a FastAPI app and run it on localhost port 8000 so that it returns a hello message. Commit as "Stage 0: hello server"

Stage 1: Create two routes. First is GET / that returns {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}. Second is GET /health that returns {"status": "ok"}. Commit as "Stage 1: root and health endpoints"

Stage 2: Create an in-memory list with 3 tasks. Each task has id (int), title (str), done (bool). Create GET /tasks that returns all tasks. Create GET /tasks/{id} that returns one task — if not found return 404 with {"error": "Task {id} not found"}. Commit as "Stage 2: read endpoints with 404"

Stage 3: Create POST /tasks. Validate that title is not missing or empty — if invalid return 400. If valid, create the task with next available id, done set to False, and return it with status 201. Use Pydantic for validation. Commit as "Stage 3: create with validation"

Stage 4: Create PUT /tasks/{id} — find task by id, if not found return 404, if body is empty return 400, otherwise update title and/or done and return updated task with 200. Create DELETE /tasks/{id} — if not found return 404, if found delete it and return 204 with empty body. Commit as "Stage 4: full CRUD"

Stage 5: Make sure Swagger UI is available at /docs — FastAPI provides this automatically. Commit as "Stage 5: Swagger UI"

Make sure all error responses include a JSON error message. Status codes must be correct — 200 reads, 201 create, 204 delete, 400 invalid input, 404 not found.

**What AI did better:**
ChatGPT created Pydantic models and custom error handlers at the top and reused them throughout — more professional and organized than my approach of handling things inline.

**What AI got wrong or ignored:**
Nothing major — the core functionality matched my spec pretty closely.

**What AI silently decided:**
I never asked for a custom exception handler or separate validator classes — ChatGPT added those on its own. Also used `tasks.pop(index)` instead of `tasks.remove(item)` for deletion which I didn't specify.

**What I improved in my prompt:**
Added that error responses should be plain JSON and that no extra handlers or classes are needed beyond what's specified.

## What I Learned

```
- Flask and FastAPI both build APIs but FastAPI comes with Swagger built in — no setup needed
- Uvicorn runs FastAPI the same way python app.py runs Flask
- curl is just a terminal version of what the browser does — except you can send POST, PUT, DELETE too
- Status codes are how your API talks to the client — 200 means ok, 201 means created, 204 means done but nothing to say, 400 means the request is broken, 404 means the thing doesn't exist
- Pydantic validates incoming data automatically — you define the shape, FastAPI enforces it
- GET requests can be tested in the browser but POST PUT DELETE need curl or Swagger
- In-memory means the data lives in a Python list — fast and simple but gone the moment the server stops
- The loop + if pattern for finding and updating items in a list is the same logic every database query uses under the hood
```