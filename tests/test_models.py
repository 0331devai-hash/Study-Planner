"""Unit tests for SQLAlchemy models (User, Task, Session)."""

import time
from datetime import datetime, timedelta
from models import db, User, Task, Session


def test_user_password_hashing(app):
    """Test that password hashing and validation work as expected."""
    user = User(username="hash_test", email="hash@example.com")
    user.set_password("SecurePassword123")

    assert user.password_hash != "SecurePassword123"
    assert user.check_password("SecurePassword123") is True
    assert user.check_password("WrongPassword") is False


def test_task_model_methods(app, test_user):
    """Test Task helper formatting methods and badges."""
    task = Task(
        user_id=test_user.id,
        title="Test Algorithm Review",
        priority="High",
        status="In Progress",
        total_study_time=3665,  # 1h 1m 5s
    )
    db.session.add(task)
    db.session.commit()

    assert task.get_priority_color() == "priority-high"
    assert task.get_status_badge() == "badge-info"
    assert task.formatted_study_time() == "01:01:05"


def test_session_duration_calculation(app, test_user):
    """Test timer session duration calculation."""
    task = Task(user_id=test_user.id, title="Timer Test Task")
    db.session.add(task)
    db.session.commit()

    sess = Session(task_id=task.id, user_id=test_user.id)
    sess.start()
    assert sess.end_time is None

    # Simulate 2 second study session
    sess.start_time = datetime.utcnow() - timedelta(seconds=10)
    duration = sess.stop()

    assert duration >= 10
    assert sess.end_time is not None
    assert sess.get_duration() == duration
