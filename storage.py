"""
In-memory storage for the Lite Planner App.

All data lives in module-level dicts and is lost on process restart.
The `reset()` helper is used by tests to clear state between runs.
"""

from typing import Dict, Any

# ---------------------------------------------------------------------------
# Storage containers
# ---------------------------------------------------------------------------

agents: Dict[str, Dict[str, Any]] = {}   # agent_id → agent dict
tasks: Dict[str, Dict[str, Any]] = {}    # task_id  → task dict


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def reset() -> None:
    """Clear all in-memory data.

    Intended for use in test fixtures to guarantee a clean slate before
    each test case.
    """
    agents.clear()
    tasks.clear()
