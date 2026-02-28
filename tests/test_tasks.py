"""
Comprehensive tests for task endpoints.

Tests cover:
  - Creating tasks with various configurations
  - Default values (status, priority)
  - List and filtering (by status, priority, assigned_to)
  - Getting, updating, and deleting tasks
  - Status transitions and task assignment
  - 404 and validation error handling
"""

import json
import uuid
from datetime import datetime

import pytest
from fastapi.testclient import TestClient


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _create_agent(client: TestClient, name: str = "TestAgent", role: str = "dev") -> str:
    """Helper to create an agent and return its ID."""
    response = client.post(
        "/agents",
        json={"name": name, "role": role}
    )
    assert response.status_code == 201
    return response.json()["id"]


def _create_task(
    client: TestClient,
    title: str = "Test Task",
    description: str = "Test Description",
    priority: str = None
) -> tuple:
    """Helper to create a task and return (status_code, task_dict)."""
    payload = {
        "title": title,
        "description": description,
    }
    if priority is not None:
        payload["priority"] = priority
    
    response = client.post("/tasks", json=payload)
    return response.status_code, response.json() if response.status_code == 201 else None


# ---------------------------------------------------------------------------
# Create Task Tests
# ---------------------------------------------------------------------------

def test_create_task_returns_201_with_all_fields(client: TestClient) -> None:
    """Test creating a task returns 201 with all required fields."""
    response = client.post(
        "/tasks",
        json={
            "title": "Implement feature X",
            "description": "Add feature X to the system",
            "priority": "high"
        }
    )
    
    assert response.status_code == 201
    task = response.json()
    
    # Check all required fields
    assert "id" in task
    assert task["title"] == "Implement feature X"
    assert task["description"] == "Add feature X to the system"
    assert task["priority"] == "high"
    assert "status" in task
    assert "created_at" in task
    assert "updated_at" in task
    assert "assigned_to" in task


def test_create_task_default_status_is_todo(client: TestClient) -> None:
    """Test that default task status is 'todo'."""
    response = client.post(
        "/tasks",
        json={
            "title": "New Task",
            "description": "A new task"
        }
    )
    
    assert response.status_code == 201
    task = response.json()
    assert task["status"] == "todo"


def test_create_task_default_priority_is_medium(client: TestClient) -> None:
    """Test that default priority is 'medium' when not specified."""
    response = client.post(
        "/tasks",
        json={
            "title": "Task with default priority",
            "description": "No priority specified"
        }
    )
    
    assert response.status_code == 201
    task = response.json()
    assert task["priority"] == "medium"


def test_create_task_custom_priority_high(client: TestClient) -> None:
    """Test that custom priority 'high' is accepted."""
    response = client.post(
        "/tasks",
        json={
            "title": "High priority task",
            "description": "This is important",
            "priority": "high"
        }
    )
    
    assert response.status_code == 201
    task = response.json()
    assert task["priority"] == "high"


def test_create_task_custom_priority_low(client: TestClient) -> None:
    """Test that custom priority 'low' is accepted."""
    response = client.post(
        "/tasks",
        json={
            "title": "Low priority task",
            "description": "This is not urgent",
            "priority": "low"
        }
    )
    
    assert response.status_code == 201
    task = response.json()
    assert task["priority"] == "low"


def test_create_task_invalid_priority_rejected(client: TestClient) -> None:
    """Test that invalid priority is rejected with 422."""
    response = client.post(
        "/tasks",
        json={
            "title": "Task with bad priority",
            "description": "Invalid priority",
            "priority": "urgent"  # Invalid
        }
    )
    
    assert response.status_code == 422


def test_create_task_has_created_at_timestamp(client: TestClient) -> None:
    """Test that created_at is set and updated_at is null."""
    response = client.post(
        "/tasks",
        json={
            "title": "Task for timestamp test",
            "description": "Check timestamps"
        }
    )
    
    assert response.status_code == 201
    task = response.json()
    
    # created_at should be present and valid ISO-8601
    assert task["created_at"] is not None
    assert "T" in task["created_at"]  # ISO-8601 format check
    
    # updated_at should be null on creation
    assert task["updated_at"] is None


# ---------------------------------------------------------------------------
# List & Filter Tests
# ---------------------------------------------------------------------------

def test_list_tasks_empty_when_none_exist(client: TestClient) -> None:
    """Test listing tasks returns empty list when none exist."""
    response = client.get("/tasks")
    
    assert response.status_code == 200
    assert response.json() == []


def test_list_tasks_returns_all_created(client: TestClient) -> None:
    """Test listing tasks returns all created tasks."""
    # Create 3 tasks
    task_ids = []
    for i in range(3):
        status, task = _create_task(
            client,
            title=f"Task {i}",
            description=f"Description {i}"
        )
        assert status == 201
        task_ids.append(task["id"])
    
    # List all
    response = client.get("/tasks")
    assert response.status_code == 200
    tasks = response.json()
    
    assert len(tasks) == 3
    returned_ids = [t["id"] for t in tasks]
    for task_id in task_ids:
        assert task_id in returned_ids


def test_list_tasks_filter_by_status(client: TestClient) -> None:
    """Test filtering tasks by status."""
    # Create 3 tasks
    task1_response = client.post(
        "/tasks",
        json={"title": "Task 1", "description": "Desc 1"}
    )
    task1_id = task1_response.json()["id"]
    
    task2_response = client.post(
        "/tasks",
        json={"title": "Task 2", "description": "Desc 2"}
    )
    task2_id = task2_response.json()["id"]
    
    task3_response = client.post(
        "/tasks",
        json={"title": "Task 3", "description": "Desc 3"}
    )
    task3_id = task3_response.json()["id"]
    
    # Move task2 and task3 to "in_progress"
    client.patch(f"/tasks/{task2_id}/status", json={"status": "in_progress"})
    client.patch(f"/tasks/{task3_id}/status", json={"status": "done"})
    
    # Filter by status=todo
    response = client.get("/tasks?status=todo")
    assert response.status_code == 200
    tasks = response.json()
    
    assert len(tasks) == 1
    assert tasks[0]["id"] == task1_id
    assert tasks[0]["status"] == "todo"


def test_list_tasks_filter_by_priority(client: TestClient) -> None:
    """Test filtering tasks by priority."""
    # Create tasks with different priorities
    task1 = client.post(
        "/tasks",
        json={"title": "High", "description": "Desc", "priority": "high"}
    ).json()
    
    task2 = client.post(
        "/tasks",
        json={"title": "Low", "description": "Desc", "priority": "low"}
    ).json()
    
    task3 = client.post(
        "/tasks",
        json={"title": "Medium", "description": "Desc", "priority": "medium"}
    ).json()
    
    # Filter by priority=high
    response = client.get("/tasks?priority=high")
    assert response.status_code == 200
    tasks = response.json()
    
    assert len(tasks) == 1
    assert tasks[0]["id"] == task1["id"]
    assert tasks[0]["priority"] == "high"


def test_list_tasks_filter_by_assigned_to(client: TestClient) -> None:
    """Test filtering tasks by assigned_to agent ID."""
    # Create 2 agents
    agent1_id = _create_agent(client, "Agent1", "dev")
    agent2_id = _create_agent(client, "Agent2", "qa")
    
    # Create 3 tasks
    task1 = client.post(
        "/tasks",
        json={"title": "Task1", "description": "Desc1"}
    ).json()
    
    task2 = client.post(
        "/tasks",
        json={"title": "Task2", "description": "Desc2"}
    ).json()
    
    task3 = client.post(
        "/tasks",
        json={"title": "Task3", "description": "Desc3"}
    ).json()
    
    # Assign task1 and task2 to agent1
    client.patch(f"/tasks/{task1['id']}/assign", json={"agent_id": agent1_id})
    client.patch(f"/tasks/{task2['id']}/assign", json={"agent_id": agent1_id})
    
    # Assign task3 to agent2
    client.patch(f"/tasks/{task3['id']}/assign", json={"agent_id": agent2_id})
    
    # Filter by assigned_to=agent1_id
    response = client.get(f"/tasks?assigned_to={agent1_id}")
    assert response.status_code == 200
    tasks = response.json()
    
    assert len(tasks) == 2
    task_ids = {t["id"] for t in tasks}
    assert task1["id"] in task_ids
    assert task2["id"] in task_ids


def test_list_tasks_multiple_filters_and_logic(client: TestClient) -> None:
    """Test that multiple filters use AND logic (intersection)."""
    # Create agent
    agent_id = _create_agent(client, "Agent", "dev")
    
    # Create tasks with different status/priority combinations
    t1 = client.post(
        "/tasks",
        json={"title": "T1", "description": "D1", "priority": "high"}
    ).json()
    client.patch(f"/tasks/{t1['id']}/status", json={"status": "todo"})
    client.patch(f"/tasks/{t1['id']}/assign", json={"agent_id": agent_id})
    
    t2 = client.post(
        "/tasks",
        json={"title": "T2", "description": "D2", "priority": "high"}
    ).json()
    client.patch(f"/tasks/{t2['id']}/status", json={"status": "done"})
    client.patch(f"/tasks/{t2['id']}/assign", json={"agent_id": agent_id})
    
    t3 = client.post(
        "/tasks",
        json={"title": "T3", "description": "D3", "priority": "low"}
    ).json()
    client.patch(f"/tasks/{t3['id']}/status", json={"status": "todo"})
    # t3 is not assigned
    
    # Filter: status=todo AND priority=high AND assigned_to=agent_id
    # Only t1 should match
    response = client.get(
        f"/tasks?status=todo&priority=high&assigned_to={agent_id}"
    )
    assert response.status_code == 200
    tasks = response.json()
    
    assert len(tasks) == 1
    assert tasks[0]["id"] == t1["id"]


# ---------------------------------------------------------------------------
# Get Task by ID Tests
# ---------------------------------------------------------------------------

def test_get_task_returns_200_with_correct_data(client: TestClient) -> None:
    """Test retrieving task by ID returns 200 with correct data."""
    create_response = client.post(
        "/tasks",
        json={
            "title": "Retrieve Me",
            "description": "Test task"
        }
    )
    task_id = create_response.json()["id"]
    
    response = client.get(f"/tasks/{task_id}")
    
    assert response.status_code == 200
    task = response.json()
    assert task["id"] == task_id
    assert task["title"] == "Retrieve Me"
    assert task["description"] == "Test task"


def test_get_task_returns_404_for_non_existent_id(client: TestClient) -> None:
    """Test retrieving non-existent task returns 404."""
    fake_uuid = str(uuid.uuid4())
    response = client.get(f"/tasks/{fake_uuid}")
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


# ---------------------------------------------------------------------------
# Update Task (PUT) Tests
# ---------------------------------------------------------------------------

def test_update_task_title_changes_and_updated_at_set(client: TestClient) -> None:
    """Test updating task title changes it and sets updated_at."""
    # Create task
    task = client.post(
        "/tasks",
        json={"title": "Original", "description": "Desc"}
    ).json()
    
    original_updated_at = task["updated_at"]
    
    # Update title
    response = client.put(
        f"/tasks/{task['id']}",
        json={"title": "Updated"}
    )
    
    assert response.status_code == 200
    updated_task = response.json()
    
    assert updated_task["title"] == "Updated"
    assert updated_task["updated_at"] is not None
    assert updated_task["updated_at"] != original_updated_at


def test_update_task_partial_update_only_title(client: TestClient) -> None:
    """Test partial update: only change title, description stays."""
    # Create task
    task = client.post(
        "/tasks",
        json={"title": "Title", "description": "Original Description"}
    ).json()
    
    # Update only title
    response = client.put(
        f"/tasks/{task['id']}",
        json={"title": "New Title"}
    )
    
    assert response.status_code == 200
    updated = response.json()
    
    assert updated["title"] == "New Title"
    assert updated["description"] == "Original Description"


def test_update_task_partial_update_only_description(client: TestClient) -> None:
    """Test partial update: only change description, title stays."""
    # Create task
    task = client.post(
        "/tasks",
        json={"title": "Original Title", "description": "Desc"}
    ).json()
    
    # Update only description
    response = client.put(
        f"/tasks/{task['id']}",
        json={"description": "New Description"}
    )
    
    assert response.status_code == 200
    updated = response.json()
    
    assert updated["title"] == "Original Title"
    assert updated["description"] == "New Description"


def test_update_task_partial_update_only_priority(client: TestClient) -> None:
    """Test partial update: only change priority."""
    # Create task
    task = client.post(
        "/tasks",
        json={"title": "Title", "description": "Desc", "priority": "low"}
    ).json()
    
    # Update only priority
    response = client.put(
        f"/tasks/{task['id']}",
        json={"priority": "high"}
    )
    
    assert response.status_code == 200
    updated = response.json()
    
    assert updated["priority"] == "high"
    assert updated["title"] == "Title"
    assert updated["description"] == "Desc"


def test_update_task_nonexistent_returns_404(client: TestClient) -> None:
    """Test updating non-existent task returns 404."""
    fake_uuid = str(uuid.uuid4())
    response = client.put(
        f"/tasks/{fake_uuid}",
        json={"title": "New Title"}
    )
    
    assert response.status_code == 404


def test_update_task_invalid_priority_rejected(client: TestClient) -> None:
    """Test updating task with invalid priority returns 422."""
    task = client.post(
        "/tasks",
        json={"title": "Title", "description": "Desc"}
    ).json()
    
    response = client.put(
        f"/tasks/{task['id']}",
        json={"priority": "mega_high"}  # Invalid
    )
    
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# Delete Task Tests
# ---------------------------------------------------------------------------

def test_delete_task_returns_204(client: TestClient) -> None:
    """Test deleting a task returns 204 No Content."""
    task = client.post(
        "/tasks",
        json={"title": "Delete Me", "description": "Desc"}
    ).json()
    
    response = client.delete(f"/tasks/{task['id']}")
    
    assert response.status_code == 204


def test_delete_task_task_no_longer_in_list(client: TestClient) -> None:
    """Test that deleted task no longer appears in list."""
    task = client.post(
        "/tasks",
        json={"title": "Delete Me", "description": "Desc"}
    ).json()
    task_id = task["id"]
    
    # Verify it's in the list
    response = client.get("/tasks")
    assert any(t["id"] == task_id for t in response.json())
    
    # Delete it
    delete_response = client.delete(f"/tasks/{task_id}")
    assert delete_response.status_code == 204
    
    # Verify it's no longer in the list
    response = client.get("/tasks")
    assert not any(t["id"] == task_id for t in response.json())


def test_delete_task_nonexistent_returns_404(client: TestClient) -> None:
    """Test deleting non-existent task returns 404."""
    fake_uuid = str(uuid.uuid4())
    response = client.delete(f"/tasks/{fake_uuid}")
    
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# Status Transition Tests
# ---------------------------------------------------------------------------

def test_patch_task_status_changes_status_and_sets_updated_at(client: TestClient) -> None:
    """Test PATCH /tasks/{id}/status changes status and sets updated_at."""
    task = client.post(
        "/tasks",
        json={"title": "Title", "description": "Desc"}
    ).json()
    
    original_updated_at = task["updated_at"]
    
    # Change status to in_progress
    response = client.patch(
        f"/tasks/{task['id']}/status",
        json={"status": "in_progress"}
    )
    
    assert response.status_code == 200
    updated = response.json()
    
    assert updated["status"] == "in_progress"
    assert updated["updated_at"] is not None
    assert updated["updated_at"] != original_updated_at


def test_patch_task_status_valid_transitions(client: TestClient) -> None:
    """Test all valid status values can be set."""
    task = client.post(
        "/tasks",
        json={"title": "Title", "description": "Desc"}
    ).json()
    
    valid_statuses = ["todo", "in_progress", "review", "done"]
    
    for status in valid_statuses:
        response = client.patch(
            f"/tasks/{task['id']}/status",
            json={"status": status}
        )
        
        assert response.status_code == 200
        updated = response.json()
        assert updated["status"] == status


def test_patch_task_status_invalid_status_rejected(client: TestClient) -> None:
    """Test that invalid status is rejected with 422."""
    task = client.post(
        "/tasks",
        json={"title": "Title", "description": "Desc"}
    ).json()
    
    response = client.patch(
        f"/tasks/{task['id']}/status",
        json={"status": "completed"}  # Invalid
    )
    
    assert response.status_code == 422


def test_patch_task_status_nonexistent_task_returns_404(client: TestClient) -> None:
    """Test status update for non-existent task returns 404."""
    fake_uuid = str(uuid.uuid4())
    response = client.patch(
        f"/tasks/{fake_uuid}/status",
        json={"status": "done"}
    )
    
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# Task Assignment Tests
# ---------------------------------------------------------------------------

def test_patch_task_assign_assigns_agent_task_shows_agent_info(client: TestClient) -> None:
    """Test assigning a task to an agent shows agent info."""
    agent_id = _create_agent(client, "Alice", "dev")
    task = client.post(
        "/tasks",
        json={"title": "Title", "description": "Desc"}
    ).json()
    
    # Assign
    response = client.patch(
        f"/tasks/{task['id']}/assign",
        json={"agent_id": agent_id}
    )
    
    assert response.status_code == 200
    assigned = response.json()
    
    assert assigned["assigned_to"] is not None
    assert assigned["assigned_to"]["id"] == agent_id
    assert assigned["assigned_to"]["name"] == "Alice"
    assert assigned["assigned_to"]["role"] == "dev"


def test_patch_task_assign_nonexistent_agent_returns_404(client: TestClient) -> None:
    """Test assigning to non-existent agent returns 404."""
    task = client.post(
        "/tasks",
        json={"title": "Title", "description": "Desc"}
    ).json()
    
    fake_agent_id = str(uuid.uuid4())
    response = client.patch(
        f"/tasks/{task['id']}/assign",
        json={"agent_id": fake_agent_id}
    )
    
    assert response.status_code == 404
    assert "Agent not found" in response.json()["detail"]


def test_patch_task_assign_nonexistent_task_returns_404(client: TestClient) -> None:
    """Test assigning non-existent task returns 404."""
    agent_id = _create_agent(client, "Alice", "dev")
    fake_task_id = str(uuid.uuid4())
    
    response = client.patch(
        f"/tasks/{fake_task_id}/assign",
        json={"agent_id": agent_id}
    )
    
    assert response.status_code == 404
    assert "Task not found" in response.json()["detail"]


def test_patch_task_assign_sets_updated_at(client: TestClient) -> None:
    """Test that assigning a task sets updated_at."""
    agent_id = _create_agent(client, "Bob", "qa")
    task = client.post(
        "/tasks",
        json={"title": "Title", "description": "Desc"}
    ).json()
    
    original_updated_at = task["updated_at"]
    
    response = client.patch(
        f"/tasks/{task['id']}/assign",
        json={"agent_id": agent_id}
    )
    
    assert response.status_code == 200
    assigned = response.json()
    
    assert assigned["updated_at"] is not None
    assert assigned["updated_at"] != original_updated_at


def test_patch_task_assign_then_filter_by_assigned_to_works(client: TestClient) -> None:
    """Test that filtering by assigned_to works after assignment."""
    agent_id = _create_agent(client, "Charlie", "dev")
    
    task1 = client.post(
        "/tasks",
        json={"title": "T1", "description": "D1"}
    ).json()
    
    task2 = client.post(
        "/tasks",
        json={"title": "T2", "description": "D2"}
    ).json()
    
    # Assign only task1
    client.patch(
        f"/tasks/{task1['id']}/assign",
        json={"agent_id": agent_id}
    )
    
    # Filter by assigned_to
    response = client.get(f"/tasks?assigned_to={agent_id}")
    assert response.status_code == 200
    tasks = response.json()
    
    assert len(tasks) == 1
    assert tasks[0]["id"] == task1["id"]
