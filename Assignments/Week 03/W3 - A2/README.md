# W3 - A2: Containerize Your Stack

## What is this

Same Task Manager API from W2 and W3-A1. Same endpoints, same routes, same responses. Third storage swap in a row — memory → SQLite → PostgreSQL in Docker. The API never noticed.

## Why Postgres over SQLite

SQLite is a file on disk — great for learning, not for production. PostgreSQL is a real database server: it handles multiple connections simultaneously, proper transactions, and is the same engine FlyRank and most real companies run in production. Moving from SQLite to Postgres here was literally one line — the connection URL. That's the whole point of keeping database code separate from route code.

## How to Run

Make sure Docker Desktop is running, then:

```bash
docker compose up
```

One command. App and database both start. No installing Postgres. No running two things manually. The database is created automatically, the table is created automatically, and three example tasks are seeded on the first run only.

## Environment Setup

Copy `.env.example` to `.env`:

```
DATABASE_URL=postgresql://postgres:dev@localhost:5432/tasks
```

Never commit `.env` — it's gitignored. The `.env.example` shows what variables are needed without exposing real credentials.

## Database Screenshots

### Tables
![tables](dt_screenshot.png)

### Data
![data](SELECT_QUERY_screenshot.png)

## Endpoints

```
GET    /              - API info
GET    /health        - Health check
GET    /tasks         - Get all tasks (?done= and ?search= filters supported)
GET    /tasks/{id}    - Get task by ID
POST   /tasks         - Create a task
PUT    /tasks/{id}    - Update title or done status
DELETE /tasks/{id}    - Remove a task
GET    /stats         - Total, done, and open task counts
```

## Status Codes

```
200 - Success
201 - Task created
204 - Task deleted, nothing to return
400 - Bad request
404 - Not found
```

## curl Example

```bash
curl -i -X POST http://localhost:8000/tasks -H "Content-Type: application/json" -d '{"title":"Buy milk"}'
```

```
HTTP/1.1 201 Created
{"id":4,"title":"Buy milk","done":false}
```

## Proving Persistence

Created a task via the API. Ran `docker compose down` — everything stopped. Ran `docker compose up` — everything restarted. The task was still there. Data survives because Postgres stores it in a named Docker volume (`taskdata`), not in the container itself. Kill the container, the data stays.

Verified directly in Postgres:

```bash
docker exec -it taskdb psql -U postgres -d tasks -c "SELECT * FROM tasks;"
```

## What Actually Clicked
- Inside docker-compose, the app talks to the database using the service name `db`, not `localhost` — containers have their own internal network and find each other by name
- Passwords never go in code — `.env` keeps secrets out of Git and `.env.example` tells others what they need without exposing anything
- `__tablename__ = "tasks"` matters — without it SQLModel names the table after the class and you end up with a table called `task` instead of `tasks`