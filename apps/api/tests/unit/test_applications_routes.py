"""Tests for applications route handlers (api/routes/applications.py).

Covers application listing (with status filtering and counts),
application creation (including duplicate prevention and job validation),
and individual application retrieval.
"""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import HTTPException

from api.routes.applications import (
    create_application,
    list_applications,
    get_application,
    _build_application_response,
)
from api.schemas.application import ApplicationCreate


class TestBuildApplicationResponse:
    """Tests for the _build_application_response helper function."""

    def test_builds_response_with_job(self, mock_application, mock_job):
        """_build_application_response should create an ApplicationResponse with nested job."""
        result = _build_application_response(mock_application, mock_job)
        assert result.id == mock_application.id
        assert result.status == "attiva"
        assert result.status_detail == "In valutazione"
        assert result.job.id == mock_job.id
        assert result.job.title == "Senior Python Developer"
        assert result.job.tags == ["Python", "FastAPI", "PostgreSQL"]


class TestCreateApplication:
    """Tests for the POST /applications endpoint."""

    @pytest.mark.asyncio
    async def test_create_application(self, mock_db, mock_user, mock_job):
        """Creating an application should link the user to the job and return the response."""
        # Setup: job exists, no existing application
        job_query_mock = MagicMock()
        app_query_mock = MagicMock()

        call_count = 0

        def query_side_effect(model):
            nonlocal call_count
            call_count += 1
            q = MagicMock()
            if call_count == 1:
                # First query: Job lookup
                q.filter.return_value.first.return_value = mock_job
            else:
                # Second query: Duplicate check
                q.filter.return_value.first.return_value = None
            return q

        mock_db.query.side_effect = query_side_effect

        def mock_refresh(app):
            app.id = str(uuid4())
            app.applied_at = datetime(2024, 7, 1, tzinfo=timezone.utc)
            app.updated_at = None
            app.recruiter_name = None
            app.recruiter_role = None

        mock_db.refresh.side_effect = mock_refresh

        data = ApplicationCreate(job_id=mock_job.id)

        result = await create_application(
            data=data, current_user=mock_user, db=mock_db
        )

        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        assert result.job.id == mock_job.id
        assert result.status == "attiva"

    @pytest.mark.asyncio
    async def test_create_application_job_not_found(self, mock_db, mock_user):
        """Creating an application for a non-existent job should raise HTTP 404."""
        mock_db.query.return_value.filter.return_value.first.return_value = None

        data = ApplicationCreate(job_id="nonexistent-job-id")

        with pytest.raises(HTTPException) as exc_info:
            await create_application(
                data=data, current_user=mock_user, db=mock_db
            )
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Job not found"

    @pytest.mark.asyncio
    async def test_create_application_duplicate_returns_409(
        self, mock_db, mock_user, mock_job, mock_application
    ):
        """Creating a duplicate application for the same job should raise HTTP 409."""
        call_count = 0

        def query_side_effect(model):
            nonlocal call_count
            call_count += 1
            q = MagicMock()
            if call_count == 1:
                # First query: Job lookup - job found
                q.filter.return_value.first.return_value = mock_job
            else:
                # Second query: Duplicate check - existing application found
                q.filter.return_value.first.return_value = mock_application
            return q

        mock_db.query.side_effect = query_side_effect

        data = ApplicationCreate(job_id=mock_job.id)

        with pytest.raises(HTTPException) as exc_info:
            await create_application(
                data=data, current_user=mock_user, db=mock_db
            )
        assert exc_info.value.status_code == 409
        assert exc_info.value.detail == "Already applied to this job"


class TestListApplications:
    """Tests for the GET /applications endpoint."""

    @pytest.mark.asyncio
    async def test_list_applications_returns_items(
        self, mock_db, mock_user, mock_application, mock_job
    ):
        """list_applications should return the user's applications with status counts."""
        # Mock counts query
        mock_db.query.return_value.filter.return_value.group_by.return_value.all.return_value = [
            ("attiva", 2),
            ("proposta", 1),
        ]

        # Mock join query
        join_mock = MagicMock()
        mock_db.query.return_value.join.return_value = join_mock
        join_mock.filter.return_value = join_mock
        join_mock.order_by.return_value.all.return_value = [
            (mock_application, mock_job),
        ]

        result = await list_applications(
            status_filter=None, current_user=mock_user, db=mock_db
        )

        assert result.total == 1
        assert len(result.items) == 1
        assert result.items[0].job.title == "Senior Python Developer"

    @pytest.mark.asyncio
    async def test_list_applications_with_status_filter(
        self, mock_db, mock_user, mock_application, mock_job
    ):
        """list_applications with status filter should apply an additional .filter call."""
        mock_db.query.return_value.filter.return_value.group_by.return_value.all.return_value = [
            ("attiva", 1),
        ]

        join_mock = MagicMock()
        mock_db.query.return_value.join.return_value = join_mock
        join_mock.filter.return_value = join_mock

        # The status filter chains another .filter
        join_mock.filter.return_value = join_mock
        join_mock.order_by.return_value.all.return_value = [
            (mock_application, mock_job),
        ]

        result = await list_applications(
            status_filter="attiva", current_user=mock_user, db=mock_db
        )

        assert result.total == 1
        assert len(result.items) == 1

    @pytest.mark.asyncio
    async def test_list_applications_empty(self, mock_db, mock_user):
        """list_applications should return empty when user has no applications."""
        mock_db.query.return_value.filter.return_value.group_by.return_value.all.return_value = []

        join_mock = MagicMock()
        mock_db.query.return_value.join.return_value = join_mock
        join_mock.filter.return_value = join_mock
        join_mock.order_by.return_value.all.return_value = []

        result = await list_applications(
            status_filter=None, current_user=mock_user, db=mock_db
        )

        assert result.total == 0
        assert len(result.items) == 0
        assert result.counts == {
            "proposta": 0,
            "da_completare": 0,
            "attiva": 0,
            "archiviata": 0,
        }


class TestGetApplication:
    """Tests for the GET /applications/{application_id} endpoint."""

    @pytest.mark.asyncio
    async def test_get_application_by_id(
        self, mock_db, mock_user, mock_application, mock_job
    ):
        """get_application should return the application with its job when found."""
        join_mock = MagicMock()
        mock_db.query.return_value.join.return_value = join_mock
        join_mock.filter.return_value.first.return_value = (
            mock_application,
            mock_job,
        )

        result = await get_application(
            application_id=mock_application.id,
            current_user=mock_user,
            db=mock_db,
        )

        assert result.id == mock_application.id
        assert result.job.id == mock_job.id

    @pytest.mark.asyncio
    async def test_get_application_not_found(self, mock_db, mock_user):
        """get_application with non-existent ID should raise HTTP 404."""
        join_mock = MagicMock()
        mock_db.query.return_value.join.return_value = join_mock
        join_mock.filter.return_value.first.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            await get_application(
                application_id="nonexistent-id",
                current_user=mock_user,
                db=mock_db,
            )
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Application not found"
