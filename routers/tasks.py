"""
Task management endpoints.

Prefix: /tasks
Routes:
  POST   /tasks                    — create a task
  GET    /tasks                    — list tasks (filterable)
  GET    /tasks/{task_id}          — get a single task or 404
  PUT    /tasks/{task_id}          — update task fields
  DELETE /tasks/{task_id}          — delete a task (204)
  PATCH  /tasks/{task_id}/status   — transition task status
  PATCH  /tasks/{task_id}/assign   — assign task to an agent

NOTE: The two PATCH sub-routes (/status, /assign) MUST be declared BEFORE
the generic /{task_id} GET/PUT/DELETE routes to avoid FastAPI matching the
literal strings "status" or "assign" as the task_id path parameter.
"""

import uuid
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import Response

from planner_app import storage
from planner_app.models import (
    Agent,
    AssignUpdate,
    StatusUpdate,
    Task,
    TaskCreate,
    TaskUpdate,
)

router = APIRouter(prefix="/tasks", tags=["tasks"])


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _now_iso() -> str:
    """Return the current UTC time as an ISO-8601 string."""
    return datetime.now(tz=timezone.utc).isoformat()


def _task_from_dict(d: dict) -> Task:
    """Convert a raw storage dict into a Task response model.

    Args:
        d: The raw task dictionary from storage.

    Returns:
        A fully-populated Task Pydantic model.
    """
    assigned: Optional[Agent] = None
    if d.get("assigned_to") is not None:
        a = d["assigned_to"]
        assigned = Agent(id=a["id"], name=a["name"], role=a["role"])

    return Task(
        id=d["id"],
        title=d["title"],
        description=d["description"],
        priority=d["priority"],
        status=d["status"],
        created_at=d["created_at"],
        updated_at=d.get("updated_at"),
        assigned_to=assigned,
    )


def _get_task_or_404(task_id: str) -> dict:
    """Fetch a task from storage or raise HTTP 404.

    Args:
        task_id: UUID of the task.

    Returns:
        The raw task dict.

    Raises:
        HTTPException 404: If the task does not exist.
    """
    record = storage.tasks.get(task_id)
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    return record


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("", response_model=Task, status_code=status.HTTP_201_CREATED)
def create_task(body: TaskCreate) -> Task:
    """Create a new task with default status 'todo' and no assignee.

    Args:
        body: TaskCreate payload with title, description, and optional priority.

    Returns:
        The newly created Task.
    """
    task_id = str(uuid.uuid4())
    record: dict = {
        "id": task_id,
        "title": body.title,
        "description": body.description,
        "priority": body.priority,
        "status": "todo",
        "created_at": _now_iso(),
        "updated_at": None,
        "assigned_to": None,
    }
    storage.tasks[task_id] = record
    return _task_from_dict(record)


@router.get("", response_model=List[Task])
def list_tasks(
    status_filter: Optional[str] = Query(default=None, alias="status", description="Filter by task status"),
    assigned_to: Optional[str] = Query(default=None, description="Filter by agent ID"),
    priority: Optional[str] = Query(default=None, description="Filter by priority"),
) -> List[Task]:
    """Return all tasks, with optional AND-combined filters.

    Query Params:
        status:      Filter to only tasks with this status.
        assigned_to: Filter to only tasks assigned to this agent_id.
        priority:    Filter to only tasks with this priority level.

    Returns:
        A (possibly empty) list of Task objects matching all supplied filters.
    """
    results = list(storage.tasks.values())

    if status_filter is not None:
        results = [t for t in results if t["status"] == status_filter]

    if assigned_to is not None:
        results = [
            t for t in results
            if t.get("assigned_to") is not None
            and t["assigned_to"]["id"] == assigned_to
        ]

    if priority is not None:
        results = [t for t in results if t["priority"] == priority]

    return [_task_from_dict(t) for t in results]


# IMPORTANT: /status and /assign MUST come before /{task_id} so FastAPI does
# not interpret the literal string "status" or "assign" as a task_id.

@router.patch("/{task_id}/status", response_model=Task)
def update_task_status(task_id: str, body: StatusUpdate) -> Task:
    """Transition a task to a new status.

    Args:
        task_id: UUID of the task to update.
        body:    StatusUpdate payload containing the new status string.

    Returns:
        The updated Task.

    Raises:
        HTTPException 404: If no task with the given ID exists.
    """
    record = _get_task_or_404(task_id)
    record["status"] = body.status
    record["updated_at"] = _now_iso()
    return _task_from_dict(record)


@router.patch("/{task_id}/assign", response_model=Task)
def assign_task(task_id: str, body: AssignUpdate) -> Task:
    """Assign a task to an agent.

    Args:
        task_id: UUID of the task to assign.
        body:    AssignUpdate payload containing the agent_id.

    Returns:
        The updated Task with assigned_to populated.

    Raises:
        HTTPException 404: If the task does not exist (detail: "Task not found").
        HTTPException 404: If the agent does not exist (detail: "Agent not found").
    """
    record = _get_task_or_404(task_id)

    agent = storage.agents.get(body.agent_id)
    if agent is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found",
        )

    record["assigned_to"] = {
        "id": agent["id"],
        "name": agent["name"],
        "role": agent["role"],
    }
    record["updated_at"] = _now_iso()
    return _task_from_dict(record)


@router.get("/{task_id}", response_model=Task)
def get_task(task_id: str) -> Task:
    """Retrieve a single task by ID.

    Args:
        task_id: UUID of the task to retrieve.

    Returns:
        The matching Task.

    Raises:
        HTTPException 404: If no task with the given ID exists.
    """
    return _task_from_dict(_get_task_or_404(task_id))


@router.put("/{task_id}", response_model=Task)
def update_task(task_id: str, body: TaskUpdate) -> Task:
    """Update one or more fields of an existing task.

    Only non-None fields in the request body are applied.
    updated_at is refreshed whenever a change is made.

    Args:
        task_id: UUID of the task to update.
        body:    TaskUpdate payload (all fields optional).

    Returns:
        The updated Task.

    Raises:
        HTTPException 404: If no task with the given ID exists.
    """
    record = _get_task_or_404(task_id)

    if body.title is not None:
        record["title"] = body.title
    if body.description is not None:
        record["description"] = body.description
    if body.priority is not None:
        record["priority"] = body.priority

    record["updated_at"] = _now_iso()
    return _task_from_dict(record)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: str) -> Response:
    """Delete a task by ID.

    Args:
        task_id: UUID of the task to delete.

    Returns:
        HTTP 204 No Content on success.

    Raises:
        HTTPException 404: If no task with the given ID exists.
    """
    _get_task_or_404(task_id)   # raises 404 if missing
    del storage.tasks[task_id]
    return Response(status_code=status.HTTP_204_NO_CONTENT)
