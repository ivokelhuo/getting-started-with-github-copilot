"""
Pytest configuration and fixtures for backend tests.

This module provides shared fixtures for testing the FastAPI application,
including a TestClient and activity state reset between tests.
"""

import sys
import copy
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

# Add src to path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities


@pytest.fixture
def client():
    """
    Fixture: Provide a TestClient for API testing.
    
    Returns a FastAPI TestClient configured to test the application.
    """
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """
    Fixture: Reset activities state before each test (autouse).
    
    This fixture automatically runs before every test to ensure a clean
    state. It preserves the original activities data and restores it
    after the test completes using a deep copy to preserve nested data.
    """
    # Arrange: Save the original state with deep copy
    original = copy.deepcopy(activities)
    
    yield
    
    # Assert/Cleanup: Restore the original state
    activities.clear()
    activities.update(copy.deepcopy(original))
