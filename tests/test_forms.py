"""Unit tests for WTForms validation classes."""

from forms import RegisterForm, LoginForm, TaskForm
from models import User, db


def test_register_form_validation(app, test_user):
    """Test registration form validations."""
    with app.app_context():
        # Duplicate username
        form_dup_user = RegisterForm(
            username="unittest_user",
            email="newemail@example.com",
            password="Password123!",
            confirm_password="Password123!",
        )
        assert form_dup_user.validate() is False
        assert "Username is already taken. Please choose another." in form_dup_user.username.errors

        # Duplicate email
        form_dup_email = RegisterForm(
            username="unique_user_99",
            email="unittest@example.com",
            password="Password123!",
            confirm_password="Password123!",
        )
        assert form_dup_email.validate() is False
        assert "An account with this email address already exists." in form_dup_email.email.errors

        # Password mismatch
        form_mismatch = RegisterForm(
            username="unique_user_99",
            email="valid@example.com",
            password="Password123!",
            confirm_password="DifferentPassword!",
        )
        assert form_mismatch.validate() is False
        assert "Passwords must match." in form_mismatch.confirm_password.errors


def test_task_form_validation(app):
    """Test task creation form validation rules."""
    with app.app_context():
        # Empty title
        form_empty = TaskForm(title="", priority="Medium", status="Pending")
        assert form_empty.validate() is False
        assert "Task title is required." in form_empty.title.errors

        # Valid task form
        form_valid = TaskForm(title="Study Discrete Mathematics", priority="High", status="Pending")
        assert form_valid.validate() is True
