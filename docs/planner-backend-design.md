# Lite Planner App — Backend Architecture

## Overview

A lightweight FastAPI application providing REST endpoints for managing agents and tasks on a simple planning board. All data is stored in-memory (process-lifetime only). The API is fronted by a single-page HTML frontend served at `GET /`.

---

## Components

| Component | Path | Role |
|---|---|---|
| `main.py` | `/planner_app/main.py` | FastAPI app factory; mounts all routers; serves frontend at `GET /` |
| `models.py` | `/planner_app/models.py` | Pydantic v2 request + response models with field validation |
| `storage.py` | `/planner_app/storage.py` | Module-level `agents` and `tasks` dicts; `reset()` for tests |
| `routers/agents.py` | `/planner_app/routers/agents.py` | Agent CRUD (3 endpoints) |
| `routers/tasks.py` | `/planner_app/routers/tasks.py` | Task CRUD + status/assign actions (8 endpoints) |
| `routers/dashboard.py` | `/planner_app/routers/dashboard.py` | Dashboard summary (1 endpoint) |
| `tests/conftest.py` | `/planner_app/tests/conftest.py` | `TestClient` fixture; `autouse` storage reset |

---

## Data Flow

```
Client HTTP Request
        │
        ▼
  FastAPI (main.py)
        │
        ├──▶ /agents    ──▶ routers/agents.py    ──▶ storage.agents dict
        │
        ├──▶ /tasks     ──▶ routers/tasks.py     ──▶ storage.tasks dict
        │                                                   │
        │                                              (assign reads)
        │                                           storage.agents dict
        ├──▶ /dashboard ──▶ routers/dashboard.py  ──▶ storage.tasks dict (read-only)
        │
        └──▶ /          ──▶ main.py (HTMLResponse)
```

---

## API Contracts

### Agents — prefix `/agents`

| Method | Path | Body | Response | Notes |
|---|---|---|---|---|
| POST | `/agents` | `{name, role}` | `201 Agent` | UUID auto-generated |
| GET | `/agents` | — | `200 Agent[]` | — |
| GET | `/agents/{agent_id}` | — | `200 Agent` / `404` | — |

### Tasks — prefix `/tasks`

| Method | Path | Body / Query | Response | Notes |
|---|---|---|---|---|
| POST | `/tasks` | `{title, description, priority?}` | `201 Task` | status=todo, assigned_to=null |
| GET | `/tasks` | `?status=&assigned_to=&priority=` | `200 Task[]` | AND-combined filters |
| GET | `/tasks/{task_id}` | — | `200 Task` / `404` | — |
| PUT | `/tasks/{task_id}` | `{title?, description?, priority?}` | `200 Task` / `404` | Refreshes updated_at |
| DELETE | `/tasks/{task_id}` | — | `204` / `404` | No response body |
| PATCH | `/tasks/{task_id}/status` | `{status}` | `200 Task` / `404` | Validates status enum |
| PATCH | `/tasks/{task_id}/assign` | `{agent_id}` | `200 Task` / `404` | 404 if task OR agent missing |

### Dashboard — prefix `/dashboard`

| Method | Path | Response |
|---|---|---|
| GET | `/dashboard` | `{total, by_status: {todo,in_progress,review,done}, by_priority: {low,medium,high}}` |

### Frontend

| Method | Path | Response |
|---|---|---|
| GET | `/` | `200 text/html` — placeholder page; full SPA delivered by SR1 |

---

## Data Model

### Agent (in-memory dict)
```python
{
  "id":   str,   # uuid4
  "name": str,
  "role": str,
}
```

### Task (in-memory dict)
```python
{
  "id":          str,           # uuid4
  "title":       str,
  "description": str,
  "priority":    str,           # "low" | "medium" | "high"
  "status":      str,           # "todo" | "in_progress" | "review" | "done"
  "created_at":  str,           # ISO-8601 UTC
  "updated_at":  str | None,    # ISO-8601 UTC, set on first mutation
  "assigned_to": dict | None,   # {id, name, role} snapshot at assignment time
}
```

---

## Non-Functional Considerations

### Security
- No authentication (out of scope for lite version). Add API key / OAuth2 in v2.
- Pydantic validation on all request bodies prevents malformed enum values from reaching storage.

### Performance
- In-memory dict lookups are O(1) for single-entity operations.
- `GET /tasks` list scans are O(n) — acceptable for a lite app.

### Scalability
- In-memory storage does not survive restarts and is not shared across processes. For production: replace `storage.py` with a PostgreSQL-backed repository layer behind an abstract interface (no router changes required).

---

## Design Decisions

### Route Ordering in tasks.py
`PATCH /tasks/{task_id}/status` and `PATCH /tasks/{task_id}/assign` are declared **before** `GET /tasks/{task_id}` / `PUT` / `DELETE`. This is critical — FastAPI matches routes in declaration order, and the literal strings `"status"` / `"assign"` would otherwise be consumed as the `task_id` path parameter.

### Query Parameter Shadow Fix
`GET /tasks` uses `status_filter` as the Python parameter name with `alias="status"` in the `Query(...)` descriptor. This avoids shadowing the imported `fastapi.status` module, which is used throughout the same file for HTTP status codes.

### assigned_to Snapshot
When `PATCH /tasks/{id}/assign` is called, agent fields (`id`, `name`, `role`) are copied into the task dict. This means task history reflects the agent's state at assignment time — a safe default for a lite planner.
