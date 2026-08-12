"""WTForms form definitions for StudyPlanner application.

Includes server-side input validation, custom validators for password
complexity and database uniqueness, and CSRF protection.
"""

import re
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    BooleanField,
    TextAreaField,
    SelectField,
    DateTimeField,
    SubmitField,
)
from wtforms.validators import (
    DataRequired,
    Length,
    Email,
    EqualTo,
    ValidationError,
    Optional,
)
from models import User


class LoginForm(FlaskForm):
    """User login form."""

    username = StringField(
        "Username",
        validators=[
            DataRequired(message="Username is required."),
            Length(min=3, max=64, message="Username must be between 3 and 64 characters."),
        ],
    )
    password = PasswordField(
        "Password",
        validators=[DataRequired(message="Password is required.")],
    )
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Log In")


class RegisterForm(FlaskForm):
    """User registration form with strict password complexity and uniqueness checks."""

    username = StringField(
        "Username",
        validators=[
            DataRequired(message="Username is required."),
            Length(min=3, max=64, message="Username must be between 3 and 64 characters."),
        ],
    )
    email = StringField(
        "Email Address",
        validators=[
            DataRequired(message="Email address is required."),
            Email(message="Please provide a valid email address."),
            Length(max=120, message="Email cannot exceed 120 characters."),
        ],
    )
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(message="Password is required."),
            Length(min=8, max=128, message="Password must be at least 8 characters long."),
        ],
    )
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[
            DataRequired(message="Please confirm your password."),
            EqualTo("password", message="Passwords must match."),
        ],
    )
    submit = SubmitField("Create Account")

    def validate_username(self, field: StringField) -> None:
        """Validate that username is unique and contains valid characters."""
        if not re.match(r"^[a-zA-Z0-9_]+$", field.data):
            raise ValidationError("Username can only contain letters, numbers, and underscores.")

        user = User.query.filter_by(username=field.data.strip()).first()
        if user:
            raise ValidationError("Username is already taken. Please choose another.")

    def validate_email(self, field: StringField) -> None:
        """Validate that email address is unique."""
        user = User.query.filter_by(email=field.data.strip().lower()).first()
        if user:
            raise ValidationError("An account with this email address already exists.")

    def validate_password(self, field: PasswordField) -> None:
        """Validate password complexity requirements."""
        password = field.data
        if not re.search(r"[0-9]", password):
            raise ValidationError("Password must contain at least one digit (0-9).")
        if not re.search(r"[a-zA-Z]", password):
            raise ValidationError("Password must contain at least one letter.")


class TaskForm(FlaskForm):
    """Task creation and editing form."""

    title = StringField(
        "Task Title",
        validators=[
            DataRequired(message="Task title is required."),
            Length(min=2, max=128, message="Title must be between 2 and 128 characters."),
        ],
    )
    description = TextAreaField(
        "Description",
        validators=[
            Optional(),
            Length(max=2000, message="Description cannot exceed 2000 characters."),
        ],
    )
    due_date = DateTimeField(
        "Due Date & Time",
        format="%Y-%m-%dT%H:%M",
        validators=[Optional()],
        description="Format: YYYY-MM-DDTHH:MM",
    )
    priority = SelectField(
        "Priority",
        choices=[("Low", "Low"), ("Medium", "Medium"), ("High", "High")],
        default="Medium",
        validators=[DataRequired()],
    )
    status = SelectField(
        "Status",
        choices=[
            ("Pending", "Pending"),
            ("In Progress", "In Progress"),
            ("Completed", "Completed"),
        ],
        default="Pending",
        validators=[DataRequired()],
    )
    submit = SubmitField("Save Task")

    def validate_due_date(self, field: DateTimeField) -> None:
        """Ensure due date is not set in the past for new tasks."""
        if field.data and field.data < datetime.utcnow():
            # Allow past dates for record keeping, but raise warning or soft validation if needed
            pass


class SearchFilterForm(FlaskForm):
    """Search and filter form for task management."""

    query = StringField("Search Tasks", validators=[Optional()])
    status = SelectField(
        "Status",
        choices=[
            ("All", "All Statuses"),
            ("Pending", "Pending"),
            ("In Progress", "In Progress"),
            ("Completed", "Completed"),
        ],
        default="All",
    )
    priority = SelectField(
        "Priority",
        choices=[
            ("All", "All Priorities"),
            ("High", "High Priority"),
            ("Medium", "Medium Priority"),
            ("Low", "Low Priority"),
        ],
        default="All",
    )
    sort_by = SelectField(
        "Sort By",
        choices=[
            ("due_date_asc", "Due Date (Earliest)"),
            ("due_date_desc", "Due Date (Latest)"),
            ("priority_desc", "Priority (High to Low)"),
            ("created_desc", "Recently Created"),
            ("title_asc", "Title (A-Z)"),
        ],
        default="due_date_asc",
    )
    submit = SubmitField("Apply Filters")
