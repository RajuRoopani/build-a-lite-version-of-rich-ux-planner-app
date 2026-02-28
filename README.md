# Lite Planner App

A lightweight Kanban-style project planner built with **FastAPI** (backend) and a **vanilla JavaScript SPA** (frontend). Create agents, manage tasks through status columns, and monitor progress on a dark-themed dashboard.

![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688)

---

## Features

- **Agent Management** — Create team members with name and role
- **Task CRUD** — Create, read, update, and delete tasks with title, description, and priority
- **Status Workflow** — Move tasks through Todo → In Progress → Review → Done
- **Task Assignment** — Assign tasks to agents; reassign at any time
- **Dashboard Stats** — Real-time aggregate counts by status and priority
- **Filtering** — Filter tasks by status, priority, and assigned agent (AND logic)
- **Dark-Themed SPA** — Responsive Kanban board with drag-and-drop, modals, and toast notifications
- **Mobile Responsive** — Tab-strip layout on mobile, 2-column on tablet, 4-column on desktop

---

## Quick Start

### Prerequisites

- Python 3.10+
- pip

### Installation

```bash
# Clone the repository
git clone https://github.com/RajuRoopani/build-a-lite-version-of-rich-ux-planner-app.git
cd build-a-lite-version-of-rich-ux-planner-app

# Install dependencies
pip install -r requirements.txt
```

### Run the Server

```bash
uvicorn planner_app.main:app --reload
```

Open [http://localhost:8000](http://localhost:8000) for the frontend SPA.
Open [http://localhost:8000/docs](http://localhost:8000/docs) for the interactive API docs.

---

## API Endpoints

### Agents

| Method | Endpoint              | Description           | Status |
|--------|-----------------------|-----------------------|--------|
| POST   | `/agents`             | Create a new agent    | 201    |
| GET    | `/agents`             | List all agents       | 200    |
| GET    | `/agents/{agent_id}`  | Get agent by ID       | 200    |

### Tasks

| Method | Endpoint                    | Description                          | Status |
|--------|-----------------------------|--------------------------------------|--------|
| POST   | `/tasks`                    | Create a new task                    | 201    |
| GET    | `/tasks`                    | List tasks (filterable)              | 200    |
| GET    | `/tasks/{task_id}`          | Get task by ID                       | 200    |
| PUT    | `/tasks/{task_id}`          | Update task fields                   | 200    |
| DELETE | `/tasks/{task_id}`          | Delete a task                        | 204    |
| PATCH  | `/tasks/{task_id}/status`   | Change task status                   | 200    |
| PATCH  | `/tasks/{task_id}/assign`   | Assign task to an agent              | 200    |

### Dashboard

| Method | Endpoint     | Description              | Status |
|--------|-------------|--------------------------|--------|
| GET    | `/dashboard` | Aggregated task stats    | 200    |

### Frontend

| Method | Endpoint | Description              | Status |
|--------|----------|--------------------------|--------|
| GET    | `/`      | Serve the SPA frontend   | 200    |

### Query Parameters (GET /tasks)

| Parameter     | Type   | Description                        |
|---------------|--------|------------------------------------|
| `status`      | string | Filter by status (todo, in_progress, review, done) |
| `priority`    | string | Filter by priority (low, medium, high) |
| `assigned_to` | string | Filter by agent UUID               |

Multiple filters use **AND** logic.

---

## Data Models

### Agent
```json
{
  "id": "uuid",
  "name": "Alice",
  "role": "Senior Dev"
}
```

### Task
```json
{
  "id": "uuid",
  "title": "Fix login bug",
  "description": "Users can't log in with SSO",
  "priority": "high",
  "status": "todo",
  "created_at": "2024-01-15T10:30:00+00:00",
  "updated_at": null,
  "assigned_to": null
}
```

### Dashboard
```json
{
  "total": 12,
  "by_status": { "todo": 4, "in_progress": 3, "review": 2, "done": 3 },
  "by_priority": { "low": 3, "medium": 5, "high": 4 }
}
```

---

## Project Structure

```
planner_app/
├── __init__.py
├── main.py                 # FastAPI app + frontend route
├── models.py               # Pydantic request/response models
├── storage.py              # In-memory data store
├── requirements.txt        # Python dependencies
├── static/
│   └── index.html          # Frontend SPA (dark-themed Kanban)
├── routers/
│   ├── __init__.py
│   ├── agents.py           # Agent CRUD endpoints
│   ├── tasks.py            # Task CRUD + status/assign endpoints
│   └── dashboard.py        # Dashboard summary endpoint
├── tests/
│   ├── __init__.py
│   ├── conftest.py         # Pytest fixtures (client, storage reset)
│   ├── test_agents.py      # Agent endpoint tests (12 tests)
│   ├── test_tasks.py       # Task endpoint tests (33 tests)
│   ├── test_dashboard.py   # Dashboard endpoint tests (8 tests)
│   └── test_integration.py # Cross-feature workflow tests (10 tests)
├── designs/
│   └── planner-ux-spec.md  # UX design specification
├── docs/
│   └── planner-backend-design.md  # Backend architecture doc
└── README.md
```

---

## Running Tests

```bash
# Run all tests
pytest planner_app/tests/ -v

# Run specific test file
pytest planner_app/tests/test_tasks.py -v

# Run with coverage
pytest planner_app/tests/ --cov=planner_app --cov-report=term-missing
```

**Test coverage:** 63 tests across 4 test files covering all 12 endpoints, validation, error handling, filtering, status transitions, task assignment, dashboard aggregation, and end-to-end integration workflows.

---

## Design Decisions

1. **In-Memory Storage** — No database; data resets on restart. Simple dict-based store makes the app zero-config.
2. **UUID Identifiers** — All entities use UUID4 for globally unique, collision-free IDs.
3. **Inline SPA** — The frontend is served as a single HTML file via `GET /` — no build step, no separate server.
4. **Dark Theme** — 3-layer depth palette (#0f1117 → #1a1d27 → #22263a) with accent colors per column.
5. **Validation** — Pydantic field validators enforce valid priorities (low/medium/high) and statuses (todo/in_progress/review/done).
6. **Partial Updates** — PUT /tasks/{id} accepts optional fields; only non-null values are applied.
7. **AND Filtering** — Multiple query parameters narrow results (intersection, not union).

---

## License

MIT
