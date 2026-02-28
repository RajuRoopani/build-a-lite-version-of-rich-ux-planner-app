"""
Integration tests for the Lite Planner App.

These tests exercise cross-feature workflows that test the full lifecycle
of agents and tasks interacting together:
  - Creating agents, assigning tasks
  - Updating task metadata and status
  - Filtering and dashboard consistency
  - End-to-end workflows with multiple entities
"""

from fastapi.testclient import TestClient


def test_create_agent_create_task_assign_task(client: TestClient) -> None:
    """Workflow: Create agent → create task → assign task to agent.
    
    Verify that the task's assigned_to field correctly reflects the agent
    information after assignment.
    """
    # Create an agent
    agent_response = client.post(
        "/agents",
        json={"name": "Alice", "role": "Backend Engineer"}
    )
    assert agent_response.status_code == 201
    agent = agent_response.json()
    agent_id = agent["id"]
    
    # Create a task
    task_response = client.post(
        "/tasks",
        json={
            "title": "Implement auth",
            "description": "Add authentication to the API",
        }
    )
    assert task_response.status_code == 201
    task = task_response.json()
    task_id = task["id"]
    assert task["assigned_to"] is None  # Not yet assigned
    
    # Assign task to agent
    assign_response = client.patch(
        f"/tasks/{task_id}/assign",
        json={"agent_id": agent_id}
    )
    assert assign_response.status_code == 200
    assigned_task = assign_response.json()
    
    # Verify assigned_to contains agent info
    assert assigned_task["assigned_to"] is not None
    assert assigned_task["assigned_to"]["id"] == agent_id
    assert assigned_task["assigned_to"]["name"] == "Alice"
    assert assigned_task["assigned_to"]["role"] == "Backend Engineer"


def test_task_status_transitions_dashboard_updates(client: TestClient) -> None:
    """Workflow: Create task → transition through all statuses.
    
    Verify that the dashboard updates correctly at each status transition
    (todo → in_progress → review → done).
    """
    # Create a task (starts as todo)
    task_response = client.post(
        "/tasks",
        json={
            "title": "Feature development",
            "description": "Build new feature",
        }
    )
    task_id = task_response.json()["id"]
    
    # Check dashboard at todo
    dashboard = client.get("/dashboard").json()
    assert dashboard["by_status"]["todo"] == 1
    assert dashboard["by_status"]["in_progress"] == 0
    assert dashboard["by_status"]["review"] == 0
    assert dashboard["by_status"]["done"] == 0
    
    # Transition to in_progress
    client.patch(f"/tasks/{task_id}/status", json={"status": "in_progress"})
    dashboard = client.get("/dashboard").json()
    assert dashboard["by_status"]["todo"] == 0
    assert dashboard["by_status"]["in_progress"] == 1
    assert dashboard["by_status"]["review"] == 0
    assert dashboard["by_status"]["done"] == 0
    
    # Transition to review
    client.patch(f"/tasks/{task_id}/status", json={"status": "review"})
    dashboard = client.get("/dashboard").json()
    assert dashboard["by_status"]["todo"] == 0
    assert dashboard["by_status"]["in_progress"] == 0
    assert dashboard["by_status"]["review"] == 1
    assert dashboard["by_status"]["done"] == 0
    
    # Transition to done
    client.patch(f"/tasks/{task_id}/status", json={"status": "done"})
    dashboard = client.get("/dashboard").json()
    assert dashboard["by_status"]["todo"] == 0
    assert dashboard["by_status"]["in_progress"] == 0
    assert dashboard["by_status"]["review"] == 0
    assert dashboard["by_status"]["done"] == 1


def test_create_multiple_agents_and_tasks_with_assignments(client: TestClient) -> None:
    """Workflow: Create multiple agents, multiple tasks, assign selectively.
    
    Verify that filtering by assigned_to returns only the tasks assigned
    to a specific agent.
    """
    # Create 3 agents
    agent_ids = []
    for i in range(3):
        response = client.post(
            "/agents",
            json={"name": f"Agent {i+1}", "role": f"Role {i+1}"}
        )
        agent_ids.append(response.json()["id"])
    
    # Create 5 tasks
    task_ids = []
    for i in range(5):
        response = client.post(
            "/tasks",
            json={
                "title": f"Task {i+1}",
                "description": f"Description {i+1}",
            }
        )
        task_ids.append(response.json()["id"])
    
    # Assign tasks to agents:
    # tasks[0, 1] → agent_ids[0]
    # tasks[2, 3] → agent_ids[1]
    # tasks[4] → agent_ids[2]
    client.patch(f"/tasks/{task_ids[0]}/assign", json={"agent_id": agent_ids[0]})
    client.patch(f"/tasks/{task_ids[1]}/assign", json={"agent_id": agent_ids[0]})
    client.patch(f"/tasks/{task_ids[2]}/assign", json={"agent_id": agent_ids[1]})
    client.patch(f"/tasks/{task_ids[3]}/assign", json={"agent_id": agent_ids[1]})
    client.patch(f"/tasks/{task_ids[4]}/assign", json={"agent_id": agent_ids[2]})
    
    # Filter by assigned_to for agent_ids[0]
    response = client.get(f"/tasks?assigned_to={agent_ids[0]}")
    tasks = response.json()
    assert len(tasks) == 2
    assert all(t["assigned_to"]["id"] == agent_ids[0] for t in tasks)
    
    # Filter by assigned_to for agent_ids[1]
    response = client.get(f"/tasks?assigned_to={agent_ids[1]}")
    tasks = response.json()
    assert len(tasks) == 2
    assert all(t["assigned_to"]["id"] == agent_ids[1] for t in tasks)
    
    # Filter by assigned_to for agent_ids[2]
    response = client.get(f"/tasks?assigned_to={agent_ids[2]}")
    tasks = response.json()
    assert len(tasks) == 1
    assert tasks[0]["assigned_to"]["id"] == agent_ids[2]


def test_task_update_changes_updated_at(client: TestClient) -> None:
    """Workflow: Create task → update fields → verify updated_at changes.
    
    Ensure that updated_at timestamp is set when a task is first modified,
    and changes on subsequent modifications.
    """
    # Create a task
    create_response = client.post(
        "/tasks",
        json={
            "title": "Original Title",
            "description": "Original Description",
        }
    )
    task = create_response.json()
    task_id = task["id"]
    
    # Verify updated_at is None on creation
    assert task["updated_at"] is None
    
    # Update the task title
    update_response = client.put(
        f"/tasks/{task_id}",
        json={"title": "Updated Title"}
    )
    updated_task = update_response.json()
    
    # Verify updated_at is now set
    assert updated_task["updated_at"] is not None
    first_update_time = updated_task["updated_at"]
    
    # Get the task again and verify updated_at remains the same
    get_response = client.get(f"/tasks/{task_id}")
    retrieved_task = get_response.json()
    assert retrieved_task["updated_at"] == first_update_time


def test_create_task_delete_task_dashboard_decreases(client: TestClient) -> None:
    """Workflow: Create task → delete task → verify dashboard total decreases.
    
    Ensure that deleting a task correctly reduces the total count and
    by_status/by_priority counts.
    """
    # Create 2 tasks with different priorities
    response1 = client.post(
        "/tasks",
        json={
            "title": "Task to Delete",
            "description": "This will be deleted",
            "priority": "high",
        }
    )
    task_id_1 = response1.json()["id"]
    
    response2 = client.post(
        "/tasks",
        json={
            "title": "Task to Keep",
            "description": "This stays",
            "priority": "low",
        }
    )
    task_id_2 = response2.json()["id"]
    
    # Verify dashboard shows both tasks
    dashboard = client.get("/dashboard").json()
    assert dashboard["total"] == 2
    assert dashboard["by_priority"]["high"] == 1
    assert dashboard["by_priority"]["low"] == 1
    
    # Delete the first task
    delete_response = client.delete(f"/tasks/{task_id_1}")
    assert delete_response.status_code == 204
    
    # Verify dashboard reflects the deletion
    dashboard = client.get("/dashboard").json()
    assert dashboard["total"] == 1
    assert dashboard["by_priority"]["high"] == 0
    assert dashboard["by_priority"]["low"] == 1


def test_create_agent_assign_task_delete_task_agent_persists(client: TestClient) -> None:
    """Workflow: Create agent → assign task → delete task → agent still exists.
    
    Verify that deleting a task does not affect the agent it was assigned to.
    """
    # Create an agent
    agent_response = client.post(
        "/agents",
        json={"name": "Bob", "role": "Frontend Engineer"}
    )
    agent_id = agent_response.json()["id"]
    
    # Create and assign a task to the agent
    task_response = client.post(
        "/tasks",
        json={
            "title": "UI Work",
            "description": "Build UI components",
        }
    )
    task_id = task_response.json()["id"]
    
    client.patch(f"/tasks/{task_id}/assign", json={"agent_id": agent_id})
    
    # Delete the task
    client.delete(f"/tasks/{task_id}")
    
    # Verify the agent still exists
    agent_response = client.get(f"/agents/{agent_id}")
    assert agent_response.status_code == 200
    agent = agent_response.json()
    assert agent["id"] == agent_id
    assert agent["name"] == "Bob"
    assert agent["role"] == "Frontend Engineer"


def test_full_workflow_multiple_agents_tasks_transitions(client: TestClient) -> None:
    """Workflow: Create 3 agents + 5 tasks with mixed priorities → assign → transition.
    
    Complex scenario: verify dashboard summary is accurate after assignments
    and status transitions.
    """
    # Create 3 agents
    agents = []
    for i in range(3):
        response = client.post(
            "/agents",
            json={"name": f"Dev {i+1}", "role": f"Developer {i+1}"}
        )
        agents.append(response.json())
    
    # Create 5 tasks with mixed priorities
    priorities = ["low", "medium", "high", "high", "low"]
    tasks = []
    for i, priority in enumerate(priorities):
        response = client.post(
            "/tasks",
            json={
                "title": f"Task {i+1}",
                "description": f"Task {i+1} description",
                "priority": priority,
            }
        )
        tasks.append(response.json())
    
    # Verify initial dashboard
    dashboard = client.get("/dashboard").json()
    assert dashboard["total"] == 5
    assert dashboard["by_priority"]["low"] == 2
    assert dashboard["by_priority"]["medium"] == 1
    assert dashboard["by_priority"]["high"] == 2
    
    # Assign tasks to agents
    client.patch(f"/tasks/{tasks[0]['id']}/assign", json={"agent_id": agents[0]["id"]})
    client.patch(f"/tasks/{tasks[1]['id']}/assign", json={"agent_id": agents[0]["id"]})
    client.patch(f"/tasks/{tasks[2]['id']}/assign", json={"agent_id": agents[1]["id"]})
    client.patch(f"/tasks/{tasks[3]['id']}/assign", json={"agent_id": agents[1]["id"]})
    client.patch(f"/tasks/{tasks[4]['id']}/assign", json={"agent_id": agents[2]["id"]})
    
    # Transition some tasks to done
    client.patch(f"/tasks/{tasks[0]['id']}/status", json={"status": "done"})
    client.patch(f"/tasks/{tasks[1]['id']}/status", json={"status": "in_progress"})
    client.patch(f"/tasks/{tasks[2]['id']}/status", json={"status": "review"})
    
    # Verify final dashboard state
    dashboard = client.get("/dashboard").json()
    assert dashboard["total"] == 5
    assert dashboard["by_status"]["todo"] == 2
    assert dashboard["by_status"]["in_progress"] == 1
    assert dashboard["by_status"]["review"] == 1
    assert dashboard["by_status"]["done"] == 1
    assert dashboard["by_priority"]["low"] == 2
    assert dashboard["by_priority"]["medium"] == 1
    assert dashboard["by_priority"]["high"] == 2


def test_create_high_priority_task_filter_by_priority(client: TestClient) -> None:
    """Workflow: Create tasks with different priorities → filter by priority.
    
    Verify that filtering by priority parameter returns only matching tasks.
    """
    # Create tasks with all three priority levels
    priorities = ["low", "medium", "high"]
    task_ids = {}
    
    for priority in priorities:
        response = client.post(
            "/tasks",
            json={
                "title": f"{priority.capitalize()} Task",
                "description": f"This is a {priority} priority task",
                "priority": priority,
            }
        )
        task_ids[priority] = response.json()["id"]
    
    # Filter by high priority
    response = client.get("/tasks?priority=high")
    tasks = response.json()
    assert len(tasks) == 1
    assert tasks[0]["priority"] == "high"
    
    # Filter by low priority
    response = client.get("/tasks?priority=low")
    tasks = response.json()
    assert len(tasks) == 1
    assert tasks[0]["priority"] == "low"
    
    # Filter by medium priority
    response = client.get("/tasks?priority=medium")
    tasks = response.json()
    assert len(tasks) == 1
    assert tasks[0]["priority"] == "medium"


def test_assign_task_reassign_to_different_agent(client: TestClient) -> None:
    """Workflow: Create task → assign to agent A → reassign to agent B.
    
    Verify that reassigning a task updates the assigned_to field to the
    new agent and the previous agent is no longer associated.
    """
    # Create 2 agents
    agent_a_response = client.post(
        "/agents",
        json={"name": "Agent A", "role": "Developer"}
    )
    agent_a_id = agent_a_response.json()["id"]
    
    agent_b_response = client.post(
        "/agents",
        json={"name": "Agent B", "role": "Tester"}
    )
    agent_b_id = agent_b_response.json()["id"]
    
    # Create a task
    task_response = client.post(
        "/tasks",
        json={
            "title": "Feature Work",
            "description": "Implement feature",
        }
    )
    task_id = task_response.json()["id"]
    
    # Assign to Agent A
    client.patch(f"/tasks/{task_id}/assign", json={"agent_id": agent_a_id})
    task = client.get(f"/tasks/{task_id}").json()
    assert task["assigned_to"]["id"] == agent_a_id
    assert task["assigned_to"]["name"] == "Agent A"
    
    # Reassign to Agent B
    client.patch(f"/tasks/{task_id}/assign", json={"agent_id": agent_b_id})
    task = client.get(f"/tasks/{task_id}").json()
    assert task["assigned_to"]["id"] == agent_b_id
    assert task["assigned_to"]["name"] == "Agent B"


def test_filter_by_status_and_priority_together(client: TestClient) -> None:
    """Workflow: Create tasks with varied statuses/priorities → filter by both.
    
    Verify that filtering by both status AND priority (AND logic) returns
    only tasks matching both criteria.
    """
    # Create 4 tasks with combinations of status and priority
    task_configs = [
        ("todo", "high"),       # todo + high
        ("todo", "low"),        # todo + low
        ("done", "high"),       # done + high
        ("done", "low"),        # done + low
    ]
    
    for status, priority in task_configs:
        task_response = client.post(
            "/tasks",
            json={
                "title": f"Task {status} {priority}",
                "description": f"A {status} task with {priority} priority",
                "priority": priority,
            }
        )
        task_id = task_response.json()["id"]
        
        # If status is not todo, transition the task
        if status != "todo":
            client.patch(f"/tasks/{task_id}/status", json={"status": status})
    
    # Filter: status=todo AND priority=high
    response = client.get("/tasks?status=todo&priority=high")
    tasks = response.json()
    assert len(tasks) == 1
    assert tasks[0]["status"] == "todo"
    assert tasks[0]["priority"] == "high"
    
    # Filter: status=done AND priority=low
    response = client.get("/tasks?status=done&priority=low")
    tasks = response.json()
    assert len(tasks) == 1
    assert tasks[0]["status"] == "done"
    assert tasks[0]["priority"] == "low"
    
    # Filter: status=done AND priority=high
    response = client.get("/tasks?status=done&priority=high")
    tasks = response.json()
    assert len(tasks) == 1
    assert tasks[0]["status"] == "done"
    assert tasks[0]["priority"] == "high"
