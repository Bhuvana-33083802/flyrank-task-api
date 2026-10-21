# Task API

A small REST API that manages a to-do list — you can create, read, update and
delete tasks. Built by hand with **FastAPI** for the FlyRank Backend internship
(Week 2, Assignment A1).

Tasks are stored **in memory** (a plain Python list), so **the data resets every
time the server restarts**. There is no database — that is deliberate at this
stage, not an oversight.

## Tech

- Python 3.10+
- FastAPI (framework)
- Uvicorn (ASGI server)

## Install

```bash
python -m venv .venv

# Windows PowerShell
.\.venv\Scripts\Activate.ps1
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

## Run

One command, from the project folder, with the virtual environment active:

```bash
uvicorn main:app --reload
```

The API is now running at <http://127.0.0.1:8000>.

- Swagger UI (interactive docs): <http://127.0.0.1:8000/docs>
- ReDoc (alternative docs view): <http://127.0.0.1:8000/redoc>
- Raw OpenAPI spec: <http://127.0.0.1:8000/openapi.json>

## Endpoints

| Method | Path               | Description                                       | Success | Errors   |
| ------ | ------------------ | ------------------------------------------------- | ------- | -------- |
| GET    | `/`                | API info — name, version, available endpoints     | 200     | —        |
| GET    | `/health`          | Health check, used by monitoring tools            | 200     | —        |
| GET    | `/tasks`           | List all tasks (supports `?done=` and `?search=`) | 200     | —        |
| POST   | `/tasks`           | Create a new task                                 | 201     | 400      |
| GET    | `/tasks/{task_id}` | Get a single task by id                           | 200     | 404      |
| PUT    | `/tasks/{task_id}` | Update a task                                     | 200     | 400, 404 |
| DELETE | `/tasks/{task_id}` | Delete a task                                     | 204     | 404      |
| GET    | `/stats`           | Task counts — total, done, open                   | 200     | —        |
| POST   | `/reset`           | Restore the 3 seed tasks                          | 200     | —        |

### Status codes

| Code | Meaning                                                                                                    |
| ---- | ---------------------------------------------------------------------------------------------------------- |
| 200  | Success — here is the data                                                                                 |
| 201  | A new resource was created                                                                                 |
| 204  | Success, and there is deliberately nothing to return (empty body)                                          |
| 400  | The request was understood, but its content breaks a rule — missing or blank title                         |
| 404  | The request was fine, but that resource does not exist                                                     |
| 422  | FastAPI's default when the body can't be parsed, or a type is wrong (e.g. a number where text is expected) |

Errors are always returned as JSON. FastAPI's standard error envelope is
`{"detail": "..."}`, for example `{"detail": "Task 99 not found"}`. (The
assignment's example showed `{"error": "..."}`; `detail` is the framework's
idiomatic equivalent and is what Swagger UI documents automatically.)

### Query parameters

`GET /tasks` takes two optional **query parameters** — the part of the URL after
`?`. They filter a collection; they do not identify a resource (that is what the
path parameter `{task_id}` does).

| Parameter | Example              | What it does                        |
| --------- | -------------------- | ----------------------------------- |
| `done`    | `/tasks?done=true`   | Only finished tasks                 |
| `search`  | `/tasks?search=milk` | Tasks whose title contains the text |

Both can be combined: `/tasks?done=false&search=milk`

## Example request

Create a task and see the response headers:

```bash
curl -i -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Buy milk"}'
```

Response:

```
<!-- PASTE YOUR OWN REAL OUTPUT HERE — run the command above and copy everything,
     including the status line and headers -->
```

## Screenshot

Swagger UI, generated automatically by FastAPI from the type hints, Pydantic
models and route decorators in `main.py`:

![Swagger UI showing all endpoints](./swagger.png)

## Project structure

```
flyrank-task-api/
├── main.py            # the whole API
├── requirements.txt
├── README.md
├── .gitignore
└── swagger.png
```

## Testing on Windows PowerShell

Two things to know:

1. In PowerShell, `curl` is an alias for `Invoke-WebRequest` and behaves
   differently. Use **`curl.exe`** explicitly.
2. PowerShell strips embedded double quotes when passing arguments to native
   programs, so a JSON body written the bash way arrives malformed at the server
   (you get a `422` with "Expecting property name enclosed in double quotes").
   Use one of these instead:

```powershell
Invoke-RestMethod -Uri http://localhost:8000/tasks `
  -Method Post -ContentType "application/json" `
  -Body '{"title": "Buy milk"}'
```

```powershell
curl.exe --% -i -X POST http://localhost:8000/tasks -H "Content-Type: application/json" -d "{\"title\":\"Buy milk\"}"
```

## Notes and limitations

**Persistence.** Tasks live in a module-level Python list, so they exist only
inside the running process. Restart the server and the list is re-initialised
from source — a task I created earlier disappeared and `GET /tasks` returned
only the 3 seeded tasks, while `PUT` on the vanished id correctly returned
`404`. That is the core limitation of in-memory storage: simple and fast, but
not durable.

**PUT vs PATCH.** Strictly, `PUT` replaces the whole resource and `PATCH`
applies a partial change. `PUT /tasks/{id}` here applies only the fields you
send — a very common real-world compromise, but technically a hybrid.

**Idempotency.** `GET`, `PUT` and `DELETE` are idempotent: calling them twice
leaves the system in the same state as calling them once. `POST` is not —
calling it twice creates two tasks. That is why deleting the same task twice
correctly returns `404` the second time.

**Not included (deliberately).** No database, no authentication, no automated
tests, no pagination. All out of scope for Week 2 — the point of this
assignment was the request/response loop, CRUD, HTTP status codes, validation,
and publishing code that someone else can actually run.
