"""Database initialization script for StudyPlanner application.

Creates all database tables, seeds a default test user (testuser / test123),
and populates sample study tasks for testing and demonstration.
"""

import sys
from datetime import datetime, timedelta
from app import create_app
from models import db, User, Task, Session

app = create_app("development")


def initialize_database():
    """Create tables and seed initial data."""
    with app.app_context():
        print("Creating database tables...")
        db.create_all()

        # Check if test user already exists
        test_user = User.query.filter_by(username="testuser").first()
        if not test_user:
            print("Creating test user (username: testuser, password: test123)...")
            test_user = User(
                username="testuser",
                email="testuser@example.com",
            )
            test_user.set_password("test123")
            db.session.add(test_user)
            db.session.commit()

            print("Seeding initial study tasks...")
            sample_tasks = [
                Task(
                    user_id=test_user.id,
                    title="Review Computer Architecture Notes",
                    description="Study chapters 4 and 5 on CPU caching and pipeline optimization.",
                    due_date=datetime.utcnow() + timedelta(days=2),
                    priority="High",
                    status="In Progress",
                    total_study_time=3600,  # 1 hour
                ),
                Task(
                    user_id=test_user.id,
                    title="Database Design Capstone Draft",
                    description="Draft entity-relationship diagrams and database schema for final submission.",
                    due_date=datetime.utcnow() + timedelta(days=5),
                    priority="High",
                    status="Pending",
                    total_study_time=1800,  # 30 mins
                ),
                Task(
                    user_id=test_user.id,
                    title="Complete Machine Learning Homework 3",
                    description="Implement k-Nearest Neighbors and Decision Tree classifiers in Python.",
                    due_date=datetime.utcnow() + timedelta(days=7),
                    priority="Medium",
                    status="Pending",
                    total_study_time=0,
                ),
                Task(
                    user_id=test_user.id,
                    title="Read Software Engineering Ethics Paper",
                    description="Summarize key points for group discussion on open source licensing.",
                    due_date=datetime.utcnow() - timedelta(days=1),
                    priority="Low",
                    status="Completed",
                    total_study_time=5400,  # 1.5 hours
                ),
            ]

            db.session.add_all(sample_tasks)
            db.session.commit()
            print("Database initialized and sample data seeded successfully!")
        else:
            print("Test user already exists. Skipping seed data insertion.")


if __name__ == "__main__":
    try:
        initialize_database()
    except Exception as e:
        print(f"Error initializing database: {str(e)}", file=sys.stderr)
        sys.exit(1)
