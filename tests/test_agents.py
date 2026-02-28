"""
Comprehensive tests for agent endpoints.

Tests cover:
  - Creating agents with valid data
  - UUID format validation
  - Listing agents (empty and populated)
  - Retrieving agents by ID
  - 404 handling for non-existent agents
  - Response format and content-type validation
  - Edge cases (empty names, multiple agents)
"""

import json
import uuid
from typing import List

import pytest
from fastapi.testclient import TestClient


# ---------------------------------------------------------------------------
# Create Agent Tests
# ---------------------------------------------------------------------------

def test_create_agent_returns_201_with_agent_data(client: TestClient) -> None:
    """Test creating an agent returns 201 with id/name/role."""
    response = client.post(
        "/agents",
        json={"name": "Alice", "role": "senior_dev"}
    )
    
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["name"] == "Alice"
    assert data["role"] == "senior_dev"


def test_create_agent_generates_valid_uuid(client: TestClient) -> None:
    """Test that created agent ID is a valid UUID."""
    response = client.post(
        "/agents",
        json={"name": "Bob", "role": "junior_dev"}
    )
    
    assert response.status_code == 201
    agent_id = response.json()["id"]
    
    # This should not raise an exception
    parsed_uuid = uuid.UUID(agent_id)
    assert str(parsed_uuid) == agent_id


def test_create_agent_has_json_content_type(client: TestClient) -> None:
    """Test that response has correct content-type header."""
    response = client.post(
        "/agents",
        json={"name": "Charlie", "role": "product_manager"}
    )
    
    assert response.status_code == 201
    assert "application/json" in response.headers["content-type"]


def test_create_agent_with_empty_name(client: TestClient) -> None:
    """Test creating an agent with empty name.
    
    Note: Pydantic allows empty strings by default for str fields.
    An empty string is still a valid string. This documents the behavior.
    """
    response = client.post(
        "/agents",
        json={"name": "", "role": "dev"}
    )
    
    # Should succeed - Pydantic allows empty strings
    assert response.status_code == 201
    assert response.json()["name"] == ""


def test_create_multiple_agents_different_ids(client: TestClient) -> None:
    """Test that multiple agents get different UUIDs."""
    response1 = client.post(
        "/agents",
        json={"name": "Agent1", "role": "dev"}
    )
    response2 = client.post(
        "/agents",
        json={"name": "Agent2", "role": "dev"}
    )
    
    assert response1.status_code == 201
    assert response2.status_code == 201
    
    id1 = response1.json()["id"]
    id2 = response2.json()["id"]
    
    assert id1 != id2


# ---------------------------------------------------------------------------
# List Agents Tests
# ---------------------------------------------------------------------------

def test_list_agents_empty_when_none_exist(client: TestClient) -> None:
    """Test listing agents returns empty list when none exist."""
    response = client.get("/agents")
    
    assert response.status_code == 200
    assert response.json() == []


def test_list_agents_returns_all_created(client: TestClient) -> None:
    """Test listing agents returns all created agents."""
    # Create 3 agents
    agent_ids = []
    for i in range(3):
        response = client.post(
            "/agents",
            json={"name": f"Agent{i}", "role": f"role{i}"}
        )
        assert response.status_code == 201
        agent_ids.append(response.json()["id"])
    
    # List all
    response = client.get("/agents")
    assert response.status_code == 200
    agents = response.json()
    
    assert len(agents) == 3
    returned_ids = [a["id"] for a in agents]
    
    for agent_id in agent_ids:
        assert agent_id in returned_ids


def test_list_agents_correct_count_after_multiple_creates(client: TestClient) -> None:
    """Test that list returns correct count after creating multiple agents."""
    # Create 5 agents
    for i in range(5):
        response = client.post(
            "/agents",
            json={"name": f"Agent{i}", "role": "dev"}
        )
        assert response.status_code == 201
    
    # List and verify count
    response = client.get("/agents")
    assert response.status_code == 200
    assert len(response.json()) == 5


# ---------------------------------------------------------------------------
# Get Agent by ID Tests
# ---------------------------------------------------------------------------

def test_get_agent_returns_200_with_correct_data(client: TestClient) -> None:
    """Test retrieving agent by ID returns 200 with correct data."""
    # Create an agent
    create_response = client.post(
        "/agents",
        json={"name": "TestAgent", "role": "engineer"}
    )
    agent_id = create_response.json()["id"]
    
    # Get by ID
    response = client.get(f"/agents/{agent_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == agent_id
    assert data["name"] == "TestAgent"
    assert data["role"] == "engineer"


def test_get_agent_returns_404_for_non_existent_id(client: TestClient) -> None:
    """Test retrieving non-existent agent returns 404."""
    fake_uuid = str(uuid.uuid4())
    response = client.get(f"/agents/{fake_uuid}")
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_get_agent_all_fields_present(client: TestClient) -> None:
    """Test that get response includes all expected fields."""
    create_response = client.post(
        "/agents",
        json={"name": "FieldTest", "role": "qa"}
    )
    agent_id = create_response.json()["id"]
    
    response = client.get(f"/agents/{agent_id}")
    data = response.json()
    
    # Check all required fields are present
    assert "id" in data
    assert "name" in data
    assert "role" in data
    
    # Ensure no extra fields
    assert len(data) == 3


# ---------------------------------------------------------------------------
# Multiple Agents + List Tests
# ---------------------------------------------------------------------------

def test_list_agents_with_various_data(client: TestClient) -> None:
    """Test listing agents with diverse data."""
    test_agents = [
        {"name": "Alice Smith", "role": "backend"},
        {"name": "Bob Jones", "role": "frontend"},
        {"name": "Carol White", "role": "devops"},
    ]
    
    created_ids = set()
    for agent_data in test_agents:
        response = client.post("/agents", json=agent_data)
        assert response.status_code == 201
        created_ids.add(response.json()["id"])
    
    # List and verify all are present
    response = client.get("/agents")
    assert response.status_code == 200
    agents = response.json()
    
    assert len(agents) == 3
    returned_ids = {a["id"] for a in agents}
    assert returned_ids == created_ids
    
    # Verify data integrity
    returned_names = {a["name"] for a in agents}
    expected_names = {a["name"] for a in test_agents}
    assert returned_names == expected_names
