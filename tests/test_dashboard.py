"""
Dashboard endpoint tests for the Lite Planner App.

This module tests the GET /dashboard endpoint that returns aggregated
task statistics including:
  - total: total count of tasks
  - by_status: counts grouped by task status (todo, in_progress, review, done)
  - by_priority: counts grouped by priority (low, medium, high)

Tests verify that the dashboard correctly reflects the current state of tasks
after various operations (create, update status, delete).
"""

from fastapi.testclient import TestClient


def test_dashboard_empty_state(client: TestClient) -> None:
    """Dashboard with no tasks shows zero counts for all categories.
    
    Expected: total=0, by_status all zero, by_priority all zero.
    """
    response = client.get("/dashboard")
    assert response.status_code == 200
    
    data = response.json()
    assert data["total"] == 0
    assert data["by_status"]["todo"] == 0
    assert data["by_status"]["in_progress"] == 0
    assert data["by_status"]["review"] == 0
    assert data["by_status"]["done"] == 0
    assert data["by_priority"]["low"] == 0
    assert data["by_priority"]["medium"] == 0
    assert data["by_priority"]["high"] == 0


def test_dashboard_one_task_created(client: TestClient) -> None:
    """Dashboard after creating 1 task shows correct counts.
    
    Expected: total=1, todo=1, medium=1 (defaults), all others=0.
    """
    # Create a task with default priority (medium) and status (todo)
    client.post(
        "/tasks",
        json={
            "title": "Sample Task",
            "description": "A test task",
        }
    )
    
    response = client.get("/dashboard")
    assert response.status_code == 200
    
    data = response.json()
    assert data["total"] == 1
    assert data["by_status"]["todo"] == 1
    assert data["by_status"]["in_progress"] == 0
    assert data["by_status"]["review"] == 0
    assert data["by_status"]["done"] == 0
    assert data["by_priority"]["low"] == 0
    assert data["by_priority"]["medium"] == 1
    assert data["by_priority"]["high"] == 0


def test_dashboard_with_different_priorities(client: TestClient) -> None:
    """Dashboard correctly counts tasks with different priority levels.
    
    Create tasks with low, medium, and high priority, verify by_priority
    counts are accurate.
    """
    # Create low priority task
    client.post(
        "/tasks",
        json={
            "title": "Low Priority Task",
            "description": "Low priority work",
            "priority": "low",
        }
    )
    
    # Create medium priority task
    client.post(
        "/tasks",
        json={
            "title": "Medium Priority Task",
            "description": "Medium priority work",
            "priority": "medium",
        }
    )
    
    # Create two high priority tasks
    client.post(
        "/tasks",
        json={
            "title": "High Priority Task 1",
            "description": "High priority work 1",
            "priority": "high",
        }
    )
    client.post(
        "/tasks",
        json={
            "title": "High Priority Task 2",
            "description": "High priority work 2",
            "priority": "high",
        }
    )
    
    response = client.get("/dashboard")
    assert response.status_code == 200
    
    data = response.json()
    assert data["total"] == 4
    assert data["by_priority"]["low"] == 1
    assert data["by_priority"]["medium"] == 1
    assert data["by_priority"]["high"] == 2


def test_dashboard_status_transitions(client: TestClient) -> None:
    """Dashboard by_status counts update as task status changes.
    
    Create a task, then transition it through statuses, verifying the
    by_status counts change correctly at each step.
    """
    # Create task (starts as todo)
    create_response = client.post(
        "/tasks",
        json={
            "title": "Status Transition Task",
            "description": "Task to transition",
        }
    )
    task_id = create_response.json()["id"]
    
    # Check initial state: todo=1
    response = client.get("/dashboard")
    data = response.json()
    assert data["by_status"]["todo"] == 1
    assert data["by_status"]["in_progress"] == 0
    assert data["by_status"]["review"] == 0
    assert data["by_status"]["done"] == 0
    
    # Transition to in_progress
    client.patch(f"/tasks/{task_id}/status", json={"status": "in_progress"})
    response = client.get("/dashboard")
    data = response.json()
    assert data["by_status"]["todo"] == 0
    assert data["by_status"]["in_progress"] == 1
    assert data["by_status"]["review"] == 0
    assert data["by_status"]["done"] == 0
    
    # Transition to review
    client.patch(f"/tasks/{task_id}/status", json={"status": "review"})
    response = client.get("/dashboard")
    data = response.json()
    assert data["by_status"]["todo"] == 0
    assert data["by_status"]["in_progress"] == 0
    assert data["by_status"]["review"] == 1
    assert data["by_status"]["done"] == 0
    
    # Transition to done
    client.patch(f"/tasks/{task_id}/status", json={"status": "done"})
    response = client.get("/dashboard")
    data = response.json()
    assert data["by_status"]["todo"] == 0
    assert data["by_status"]["in_progress"] == 0
    assert data["by_status"]["review"] == 0
    assert data["by_status"]["done"] == 1


def test_dashboard_after_task_deletion(client: TestClient) -> None:
    """Dashboard total decreases when a task is deleted.
    
    Create 3 tasks, delete one, verify total decreases and remaining counts
    are correct.
    """
    # Create 3 tasks
    ids = []
    for i in range(3):
        response = client.post(
            "/tasks",
            json={
                "title": f"Task {i+1}",
                "description": f"Task description {i+1}",
                "priority": ["low", "medium", "high"][i],
            }
        )
        ids.append(response.json()["id"])
    
    # Verify total is 3
    response = client.get("/dashboard")
    data = response.json()
    assert data["total"] == 3
    assert data["by_priority"]["low"] == 1
    assert data["by_priority"]["medium"] == 1
    assert data["by_priority"]["high"] == 1
    
    # Delete the first task
    client.delete(f"/tasks/{ids[0]}")
    
    # Verify total is 2 and priority counts are correct
    response = client.get("/dashboard")
    data = response.json()
    assert data["total"] == 2
    assert data["by_priority"]["low"] == 0
    assert data["by_priority"]["medium"] == 1
    assert data["by_priority"]["high"] == 1


def test_dashboard_has_all_required_keys(client: TestClient) -> None:
    """Dashboard response has all required top-level keys.
    
    Verify the response structure contains: total, by_status, by_priority.
    """
    response = client.get("/dashboard")
    assert response.status_code == 200
    
    data = response.json()
    assert "total" in data
    assert "by_status" in data
    assert "by_priority" in data
    assert isinstance(data["total"], int)
    assert isinstance(data["by_status"], dict)
    assert isinstance(data["by_priority"], dict)


def test_dashboard_by_status_has_all_statuses(client: TestClient) -> None:
    """Dashboard by_status contains all 4 status keys.
    
    Verify: todo, in_progress, review, done are all present.
    """
    response = client.get("/dashboard")
    assert response.status_code == 200
    
    data = response.json()
    by_status = data["by_status"]
    assert "todo" in by_status
    assert "in_progress" in by_status
    assert "review" in by_status
    assert "done" in by_status
    assert len(by_status) == 4


def test_dashboard_by_priority_has_all_priorities(client: TestClient) -> None:
    """Dashboard by_priority contains all 3 priority keys.
    
    Verify: low, medium, high are all present.
    """
    response = client.get("/dashboard")
    assert response.status_code == 200
    
    data = response.json()
    by_priority = data["by_priority"]
    assert "low" in by_priority
    assert "medium" in by_priority
    assert "high" in by_priority
    assert len(by_priority) == 3
