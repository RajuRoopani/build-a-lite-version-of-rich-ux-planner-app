"""
Pydantic models for the Lite Planner App.

Request models handle validation for incoming payloads.
Response models define the shapes returned to clients.
"""

from typing import Optional
from pydantic import BaseModel, field_validator

# ---------------------------------------------------------------------------
# Validation constants
# ---------------------------------------------------------------------------

VALID_PRIORITIES = {"low", "medium", "high"}
VALID_STATUSES = {"todo", "in_progress", "review", "done"}


# ---------------------------------------------------------------------------
# Request models
# ---------------------------------------------------------------------------

class AgentCreate(BaseModel):
    """Request body for creating a new agent."""

    name: str
    role: str


class TaskCreate(BaseModel):
    """Request body for creating a new task."""

    title: str
    description: str
    priority: str = "medium"

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v: str) -> str:
        """Ensure priority is one of low / medium / high."""
        if v not in VALID_PRIORITIES:
            raise ValueError(f"priority must be one of {sorted(VALID_PRIORITIES)}")
        return v


class TaskUpdate(BaseModel):
    """Request body for updating an existing task (all fields optional)."""

    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v: Optional[str]) -> Optional[str]:
        """Ensure priority (if provided) is one of low / medium / high."""
        if v is not None and v not in VALID_PRIORITIES:
            raise ValueError(f"priority must be one of {sorted(VALID_PRIORITIES)}")
        return v


class StatusUpdate(BaseModel):
    """Request body for updating a task's status."""

    status: str

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Ensure status is one of todo / in_progress / review / done."""
        if v not in VALID_STATUSES:
            raise ValueError(f"status must be one of {sorted(VALID_STATUSES)}")
        return v


class AssignUpdate(BaseModel):
    """Request body for assigning a task to an agent."""

    agent_id: str


# ---------------------------------------------------------------------------
# Response models
# ---------------------------------------------------------------------------

class Agent(BaseModel):
    """Serialised agent returned in API responses."""

    id: str
    name: str
    role: str


class Task(BaseModel):
    """Serialised task returned in API responses."""

    id: str
    title: str
    description: str
    priority: str
    status: str
    created_at: str                     # ISO-8601 UTC timestamp
    updated_at: Optional[str] = None    # ISO-8601 UTC timestamp, set on first update
    assigned_to: Optional[Agent] = None # Nested agent info when assigned


class DashboardResponse(BaseModel):
    """Summary counts returned by the dashboard endpoint."""

    total: int
    by_status: dict
    by_priority: dict
