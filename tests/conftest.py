"""
Pytest configuration and shared fixtures for the Lite Planner App test suite.

Fixtures:
  client  — a fresh TestClient bound to the FastAPI app.
             Storage is reset before EVERY test so tests are fully isolated.
"""

import pytest
from fastapi.testclient import TestClient

from planner_app.main import app
from planner_app import storage


@pytest.fixture(autouse=True)
def reset_storage() -> None:
    """Clear all in-memory data before each test.

    Marked autouse=True so every test starts with an empty store without
    needing to explicitly request this fixture.
    """
    storage.reset()


@pytest.fixture
def client(reset_storage) -> TestClient:  # noqa: F811
    """Return a TestClient wired to the FastAPI app.

    Depends on reset_storage (implicit via autouse, but declared here
    explicitly to document the ordering guarantee).

    Returns:
        A configured httpx-backed TestClient.
    """
    return TestClient(app)
