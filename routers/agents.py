"""
Agent management endpoints.

Prefix: /agents
Routes:
  POST   /agents           — create a new agent
  GET    /agents           — list all agents
  GET    /agents/{agent_id} — get a single agent or 404
"""

import uuid
from typing import List

from fastapi import APIRouter, HTTPException, status

from planner_app import storage
from planner_app.models import Agent, AgentCreate

router = APIRouter(prefix="/agents", tags=["agents"])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _agent_from_dict(d: dict) -> Agent:
    """Convert a raw storage dict to an Agent response model."""
    return Agent(id=d["id"], name=d["name"], role=d["role"])


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("", response_model=Agent, status_code=status.HTTP_201_CREATED)
def create_agent(body: AgentCreate) -> Agent:
    """Create a new agent with an auto-generated UUID.

    Args:
        body: AgentCreate payload containing name and role.

    Returns:
        The newly created Agent with its generated id.
    """
    agent_id = str(uuid.uuid4())
    record: dict = {
        "id": agent_id,
        "name": body.name,
        "role": body.role,
    }
    storage.agents[agent_id] = record
    return _agent_from_dict(record)


@router.get("", response_model=List[Agent])
def list_agents() -> List[Agent]:
    """Return all agents currently in storage.

    Returns:
        A (possibly empty) list of Agent objects.
    """
    return [_agent_from_dict(a) for a in storage.agents.values()]


@router.get("/{agent_id}", response_model=Agent)
def get_agent(agent_id: str) -> Agent:
    """Retrieve a single agent by ID.

    Args:
        agent_id: The UUID of the agent to retrieve.

    Returns:
        The matching Agent.

    Raises:
        HTTPException 404: If no agent with the given ID exists.
    """
    record = storage.agents.get(agent_id)
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found",
        )
    return _agent_from_dict(record)
