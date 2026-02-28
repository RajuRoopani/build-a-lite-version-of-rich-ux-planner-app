"""
Lite Planner App — FastAPI application entry point.

Start with:
    uvicorn planner_app.main:app --reload

The app exposes:
  - /agents    → agent management
  - /tasks     → task CRUD + status/assign actions
  - /dashboard → summary statistics
  - /          → full Kanban SPA frontend
"""

import pathlib

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from planner_app.routers import agents, dashboard, tasks

_STATIC_DIR = pathlib.Path(__file__).resolve().parent / "static"

# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Lite Planner App",
    description="A lightweight project-planner API with agent and task management.",
    version="1.0.0",
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------

app.include_router(agents.router)
app.include_router(tasks.router)
app.include_router(dashboard.router)


# ---------------------------------------------------------------------------
# Frontend SPA (GET /)
# ---------------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse, tags=["frontend"])
def serve_frontend() -> HTMLResponse:
    """Serve the planner frontend SPA.

    Reads the static/index.html file and returns it as an HTML response.
    The SPA communicates with the API endpoints to manage agents, tasks,
    and view dashboard statistics on a dark-themed Kanban board.

    Returns:
        The complete single-page application HTML.
    """
    html_path = _STATIC_DIR / "index.html"
    return HTMLResponse(content=html_path.read_text(encoding="utf-8"), status_code=200)
