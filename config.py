"""Configuration module for StudyPlanner application.

Provides environment-specific configuration classes for Development,
Testing, and Production environments with secure defaults.
"""

import os
from datetime import timedelta

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Base configuration class with common settings."""

    # Security settings
    SECRET_KEY = os.environ.get("SECRET_KEY") or os.urandom(32).hex()

    # Database settings
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL"
    ) or f"sqlite:///{os.path.join(BASE_DIR, 'studyplanner.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Session & Cookie security
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = False  # Set to True in HTTPS production environments
    SESSION_COOKIE_SAMESITE = "Lax"
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_DURATION = timedelta(days=14)

    # WTForms / CSRF settings
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600  # 1 hour

    # Application settings
    TASKS_PER_PAGE = 10
    RATELIMIT_DEFAULT = "200 per day;50 per hour"
    RATELIMIT_STORAGE_URI = "memory://"


class DevelopmentConfig(Config):
    """Development configuration with debugging enabled."""

    DEBUG = True
    TESTING = False


class TestingConfig(Config):
    """Testing configuration using an in-memory database."""

    DEBUG = False
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False  # Simplify automated testing
    RATELIMIT_ENABLED = False


class ProductionConfig(Config):
    """Production configuration with strict security defaults."""

    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
