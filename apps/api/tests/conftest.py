"""Shared fixtures for the Datapizza Tools API test suite."""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock
from uuid import uuid4

import pytest

# Add api to path so imports work correctly
api_path = Path(__file__).parent.parent
if str(api_path) not in sys.path:
    sys.path.insert(0, str(api_path))


@pytest.fixture
def mock_db():
    """Mock SQLAlchemy session with sensible defaults.

    Returns a MagicMock that mimics a SQLAlchemy Session object.
    Default query chain returns None for .first() and [] for .all().
    """
    session = MagicMock()
    session.query.return_value.filter.return_value.first.return_value = None
    session.query.return_value.filter.return_value.all.return_value = []
    session.query.return_value.count.return_value = 0
    return session


@pytest.fixture
def mock_user():
    """Mock authenticated user with realistic Italian developer profile.

    Returns a MagicMock that mimics a SQLAlchemy User model instance with
    all fields populated with sensible test defaults.
    """
    user = MagicMock()
    user.id = str(uuid4())
    user.email = "test@email.it"
    user.password_hash = "$2b$12$fake_hash"
    user.full_name = "Test User"
    user.phone = None
    user.bio = "Test bio"
    user.location = "Milano"
    user.experience_level = "mid"
    user.experience_years = "3-5 anni"
    user.current_role = "Developer"
    user.skills_json = '["Python", "FastAPI"]'
    user.availability_status = "available"
    user.reskilling_status = None
    user.adopted_by_company = None
    user.linkedin_url = None
    user.github_url = None
    user.portfolio_url = None
    user.is_active = 1
    user.created_at = datetime(2024, 1, 1, tzinfo=timezone.utc)
    user.updated_at = datetime(2024, 1, 1, tzinfo=timezone.utc)
    return user


@pytest.fixture
def mock_job():
    """Mock job listing with realistic Italian job data.

    Returns a MagicMock that mimics a SQLAlchemy Job model instance.
    """
    job = MagicMock()
    job.id = str(uuid4())
    job.title = "Senior Python Developer"
    job.company = "TechCorp Italia"
    job.company_logo_url = None
    job.location = "Milano"
    job.work_mode = "hybrid"
    job.description = "Looking for a senior Python developer."
    job.salary_min = 45000
    job.salary_max = 65000
    job.tags_json = '["Python", "FastAPI", "PostgreSQL"]'
    job.experience_level = "senior"
    job.experience_years = "5+ anni"
    job.employment_type = "full-time"
    job.smart_working = "2-3 giorni/settimana"
    job.welfare = "Welfare aziendale di 1.000 euro"
    job.language = "Inglese: B2"
    job.apply_url = "https://example.com/apply"
    job.is_active = 1
    job.created_at = datetime(2024, 6, 1, tzinfo=timezone.utc)
    job.updated_at = datetime(2024, 6, 1, tzinfo=timezone.utc)
    return job


@pytest.fixture
def mock_news():
    """Mock news item with realistic data.

    Returns a MagicMock that mimics a SQLAlchemy News model instance.
    """
    news = MagicMock()
    news.id = str(uuid4())
    news.title = "AI Trends 2024"
    news.summary = "An overview of the latest AI trends."
    news.source = "Hacker News"
    news.source_url = "https://news.ycombinator.com/item?id=123"
    news.category = "AI"
    news.tags_json = '["AI", "Machine Learning"]'
    news.author = "John Doe"
    news.published_at = datetime(2024, 6, 15, tzinfo=timezone.utc)
    news.is_active = 1
    news.created_at = datetime(2024, 6, 15, tzinfo=timezone.utc)
    news.updated_at = datetime(2024, 6, 15, tzinfo=timezone.utc)
    return news


@pytest.fixture
def mock_course():
    """Mock course with realistic data.

    Returns a MagicMock that mimics a SQLAlchemy Course model instance.
    """
    course = MagicMock()
    course.id = str(uuid4())
    course.title = "Machine Learning with Python"
    course.description = "A comprehensive ML course."
    course.provider = "Coursera"
    course.url = "https://coursera.org/ml-python"
    course.instructor = "Andrew Ng"
    course.level = "intermediate"
    course.duration = "8 settimane"
    course.price = "Gratis"
    course.rating = "4.9"
    course.students_count = 50000
    course.category = "ML"
    course.tags_json = '["Python", "Machine Learning", "TensorFlow"]'
    course.image_url = None
    course.is_active = 1
    course.created_at = datetime(2024, 5, 1, tzinfo=timezone.utc)
    course.updated_at = datetime(2024, 5, 1, tzinfo=timezone.utc)
    return course


@pytest.fixture
def mock_experience():
    """Mock work experience with realistic data.

    Returns a MagicMock that mimics a SQLAlchemy Experience model instance.
    """
    exp = MagicMock()
    exp.id = str(uuid4())
    exp.user_id = str(uuid4())
    exp.title = "Frontend Developer"
    exp.company = "StartupXYZ"
    exp.employment_type = "full-time"
    exp.location = "Roma"
    exp.start_month = 3
    exp.start_year = 2021
    exp.end_month = None
    exp.end_year = None
    exp.is_current = 1
    exp.description = "Working on React applications."
    exp.created_at = datetime(2024, 1, 1, tzinfo=timezone.utc)
    exp.updated_at = datetime(2024, 1, 1, tzinfo=timezone.utc)
    return exp


@pytest.fixture
def mock_education():
    """Mock education entry with realistic data.

    Returns a MagicMock that mimics a SQLAlchemy Education model instance.
    """
    edu = MagicMock()
    edu.id = str(uuid4())
    edu.user_id = str(uuid4())
    edu.institution = "Politecnico di Milano"
    edu.degree = "Laurea Magistrale"
    edu.degree_type = "master"
    edu.field_of_study = "Informatica"
    edu.start_year = 2018
    edu.end_year = 2020
    edu.is_current = 0
    edu.description = "Focus on distributed systems."
    edu.created_at = datetime(2024, 1, 1, tzinfo=timezone.utc)
    edu.updated_at = datetime(2024, 1, 1, tzinfo=timezone.utc)
    return edu


@pytest.fixture
def mock_application(mock_user, mock_job):
    """Mock application linking a user to a job.

    Returns a MagicMock that mimics a SQLAlchemy Application model instance.
    """
    app = MagicMock()
    app.id = str(uuid4())
    app.user_id = mock_user.id
    app.job_id = mock_job.id
    app.status = "attiva"
    app.status_detail = "In valutazione"
    app.recruiter_name = None
    app.recruiter_role = None
    app.applied_at = datetime(2024, 7, 1, tzinfo=timezone.utc)
    app.updated_at = datetime(2024, 7, 1, tzinfo=timezone.utc)
    return app
