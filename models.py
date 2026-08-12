"""Database models for StudyPlanner application.

Includes User, Task, and Session models with SQLAlchemy ORM mappings,
Flask-Login UserMixin compliance, password hashing, and helper utilities.
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """User account model for authentication and task ownership."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    tasks = db.relationship("Task", backref="user", lazy="dynamic", cascade="all, delete-orphan")
    sessions = db.relationship("Session", backref="user", lazy="dynamic", cascade="all, delete-orphan")

    def set_password(self, password: str) -> None:
        """Hash and set the user's password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Verify the password against the stored hash."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self) -> str:
        return f"<User {self.username}>"


class Task(db.Model):
    """Study task item associated with a specific user."""

    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    title = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text, nullable=True)
    due_date = db.Column(db.DateTime, nullable=True)
    priority = db.Column(db.String(20), default="Medium", nullable=False)  # Low, Medium, High
    status = db.Column(db.String(20), default="Pending", nullable=False)  # Pending, In Progress, Completed
    total_study_time = db.Column(db.Integer, default=0, nullable=False)  # Duration in seconds
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    sessions = db.relationship("Session", backref="task", lazy="dynamic", cascade="all, delete-orphan")

    def get_status_badge(self) -> str:
        """Return CSS class for status badge rendering."""
        mapping = {
            "Pending": "badge-warning",
            "In Progress": "badge-info",
            "Completed": "badge-success",
        }
        return mapping.get(self.status, "badge-secondary")

    def get_priority_color(self) -> str:
        """Return CSS class for priority tag rendering."""
        mapping = {
            "Low": "priority-low",
            "Medium": "priority-medium",
            "High": "priority-high",
        }
        return mapping.get(self.priority, "priority-medium")

    def formatted_study_time(self) -> str:
        """Format total study time seconds into human-readable HH:MM:SS format."""
        hours, remainder = divmod(self.total_study_time, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def __repr__(self) -> str:
        return f"<Task {self.title} (User {self.user_id})>"


class Session(db.Model):
    """Active or past study timer session for a task."""

    __tablename__ = "sessions"

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey("tasks.id"), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    start_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    end_time = db.Column(db.DateTime, nullable=True)
    duration = db.Column(db.Integer, default=0, nullable=False)  # Duration in seconds

    def start(self) -> None:
        """Record session start timestamp."""
        self.start_time = datetime.utcnow()
        self.end_time = None
        self.duration = 0

    def stop(self) -> int:
        """Stop session, calculate duration in seconds, and return it."""
        self.end_time = datetime.utcnow()
        delta = self.end_time - self.start_time
        self.duration = max(0, int(delta.total_seconds()))
        return self.duration

    def get_duration(self) -> int:
        """Return current duration or elapsed seconds if session is active."""
        if self.duration > 0:
            return self.duration
        if self.start_time:
            delta = datetime.utcnow() - self.start_time
            return max(0, int(delta.total_seconds()))
        return 0

    def __repr__(self) -> str:
        return f"<Session Task={self.task_id} Duration={self.duration}s>"
