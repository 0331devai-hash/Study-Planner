"""Integration tests for application routes and endpoints."""

from models import Task, db


def test_public_routes(client):
    """Verify landing, about, and health check endpoints."""
    res_index = client.get("/")
    assert res_index.status_code == 200
    assert b"Master Your Study Schedule" in res_index.data

    res_about = client.get("/about")
    assert res_about.status_code == 200
    assert b"About StudyPlanner" in res_about.data

    res_health = client.get("/health")
    assert res_health.status_code == 200
    assert res_health.json["status"] == "healthy"


def test_login_logout_flow(client, test_user):
    """Test login and logout workflow."""
    # Attempt login with correct password
    res_login = client.post(
        "/login",
        data={"username": "unittest_user", "password": "Secret123!"},
        follow_redirects=True,
    )
    assert res_login.status_code == 200
    assert b"Welcome back, unittest_user!" in res_login.data

    # Logout
    res_logout = client.get("/logout", follow_redirects=True)
    assert res_logout.status_code == 200
    assert b"You have been logged out successfully." in res_logout.data


def test_task_crud_operations(auth_client, app, test_user):
    """Test task creation, reading, editing, and deleting."""
    # Create task
    res_create = auth_client.post(
        "/task/new",
        data={
            "title": "Integration Test Task",
            "description": "Task created during integration testing.",
            "priority": "High",
            "status": "Pending",
        },
        follow_redirects=True,
    )
    assert res_create.status_code == 200
    assert b"Task created successfully!" in res_create.data

    with app.app_context():
        task = Task.query.filter_by(title="Integration Test Task").first()
        assert task is not None
        task_id = task.id

    # Edit task
    res_edit = auth_client.post(
        f"/task/{task_id}/edit",
        data={
            "title": "Updated Integration Task",
            "description": "Updated description.",
            "priority": "Low",
            "status": "Completed",
        },
        follow_redirects=True,
    )
    assert res_edit.status_code == 200
    assert b"Task updated successfully!" in res_edit.data

    # Delete task
    res_delete = auth_client.post(f"/task/{task_id}/delete", follow_redirects=True)
    assert res_delete.status_code == 200
    assert b"Task deleted successfully." in res_delete.data


def test_timer_api_endpoints(auth_client, app, test_user):
    """Test timer start and stop API endpoints."""
    with app.app_context():
        task = Task(user_id=test_user.id, title="API Timer Test Task")
        db.session.add(task)
        db.session.commit()
        task_id = task.id

    # Start timer
    res_start = auth_client.post(f"/task/{task_id}/timer/start")
    assert res_start.status_code == 200
    assert res_start.json["success"] is True

    # Stop timer
    res_stop = auth_client.post(f"/task/{task_id}/timer/stop")
    assert res_stop.status_code == 200
    assert res_stop.json["success"] is True
