"""Pytest configuration and test fixtures for StudyPlanner.

Provides isolated application context, temporary in-memory database instance,
and pre-configured test client and authenticated user sessions.
"""

import pytest
import sys
import os

# Add root project directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from models import db, User, Task, Session


@pytest.fixture
def app():
    """Create test application instance with TestingConfig."""
    app = create_app("testing")

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Provide Flask test client."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Provide CLI runner."""
    return app.test_cli_runner()


@pytest.fixture
def test_user(app):
    """Create and return a sample database user for testing."""
    user = User(
        username="unittest_user",
        email="unittest@example.com",
    )
    user.set_password("Secret123!")
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def auth_client(client, test_user):
    """Provide a test client already authenticated as test_user."""
    client.post(
        "/login",
        data={"username": "unittest_user", "password": "Secret123!"},
        follow_redirects=True,
    )
    return client
