"""
Dashboard summary endpoint.

Prefix: /dashboard
Routes:
  GET /dashboard — return aggregate counts across all tasks
"""

from fastapi import APIRouter

from planner_app import storage
from planner_app.models import DashboardResponse

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("", response_model=DashboardResponse)
def get_dashboard() -> DashboardResponse:
    """Return aggregated task statistics.

    Counts tasks by status and by priority across all tasks currently
    in storage.

    Returns:
        DashboardResponse with:
          - total:       total number of tasks
          - by_status:   counts for todo / in_progress / review / done
          - by_priority: counts for low / medium / high
    """
    all_tasks = list(storage.tasks.values())

    by_status: dict = {"todo": 0, "in_progress": 0, "review": 0, "done": 0}
    by_priority: dict = {"low": 0, "medium": 0, "high": 0}

    for task in all_tasks:
        s = task.get("status", "todo")
        if s in by_status:
            by_status[s] += 1

        p = task.get("priority", "medium")
        if p in by_priority:
            by_priority[p] += 1

    return DashboardResponse(
        total=len(all_tasks),
        by_status=by_status,
        by_priority=by_priority,
    )
