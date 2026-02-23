"""Tests for jobs route handlers (api/routes/jobs.py).

Covers job listing with pagination, work_mode filtering,
and individual job retrieval. Note: the current routes only expose
a list_jobs endpoint (no get_job by ID endpoint in the codebase).
"""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import MagicMock, PropertyMock, call
from uuid import uuid4

import pytest

from api.routes.jobs import list_jobs


class TestListJobs:
    """Tests for the GET /jobs endpoint."""

    @pytest.mark.asyncio
    async def test_list_jobs_returns_items(self, mock_db, mock_job):
        """list_jobs should return job items with parsed tags and pagination info."""
        # Setup query chain
        query_mock = MagicMock()
        mock_db.query.return_value.filter.return_value = query_mock
        query_mock.count.return_value = 1
        query_mock.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [mock_job]

        result = await list_jobs(page=1, page_size=10, work_mode=None, db=mock_db)

        assert result.total == 1
        assert result.page == 1
        assert result.page_size == 10
        assert len(result.items) == 1

        job_resp = result.items[0]
        assert job_resp.id == mock_job.id
        assert job_resp.title == "Senior Python Developer"
        assert job_resp.company == "TechCorp Italia"
        assert job_resp.work_mode == "hybrid"
        assert job_resp.tags == ["Python", "FastAPI", "PostgreSQL"]

    @pytest.mark.asyncio
    async def test_list_jobs_empty(self, mock_db):
        """list_jobs should return an empty list when no jobs exist."""
        query_mock = MagicMock()
        mock_db.query.return_value.filter.return_value = query_mock
        query_mock.count.return_value = 0
        query_mock.order_by.return_value.offset.return_value.limit.return_value.all.return_value = []

        result = await list_jobs(page=1, page_size=10, work_mode=None, db=mock_db)

        assert result.total == 0
        assert len(result.items) == 0

    @pytest.mark.asyncio
    async def test_list_jobs_with_work_mode_filter(self, mock_db, mock_job):
        """list_jobs with work_mode filter should chain an additional .filter call."""
        query_mock = MagicMock()
        mock_db.query.return_value.filter.return_value = query_mock

        # When work_mode is provided, there's an additional .filter() call
        filtered_mock = MagicMock()
        query_mock.filter.return_value = filtered_mock
        filtered_mock.count.return_value = 1
        filtered_mock.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [mock_job]

        result = await list_jobs(page=1, page_size=10, work_mode="remote", db=mock_db)

        # The second filter is called for work_mode
        query_mock.filter.assert_called_once()
        assert result.total == 1

    @pytest.mark.asyncio
    async def test_list_jobs_pagination(self, mock_db):
        """list_jobs should apply correct offset based on page and page_size."""
        query_mock = MagicMock()
        mock_db.query.return_value.filter.return_value = query_mock
        query_mock.count.return_value = 25

        # Create 5 mock jobs for page 2
        jobs = []
        for i in range(5):
            j = MagicMock()
            j.id = str(uuid4())
            j.title = f"Job {i}"
            j.company = "Company"
            j.company_logo_url = None
            j.location = "Milano"
            j.work_mode = "remote"
            j.description = "Description"
            j.salary_min = 30000
            j.salary_max = 50000
            j.tags_json = "[]"
            j.experience_level = "mid"
            j.experience_years = "3-5 anni"
            j.employment_type = "full-time"
            j.smart_working = None
            j.welfare = None
            j.language = None
            j.apply_url = None
            j.created_at = datetime(2024, 6, 1, tzinfo=timezone.utc)
            j.updated_at = None
            jobs.append(j)

        query_mock.order_by.return_value.offset.return_value.limit.return_value.all.return_value = jobs

        result = await list_jobs(page=3, page_size=5, work_mode=None, db=mock_db)

        assert result.total == 25
        assert result.page == 3
        assert result.page_size == 5
        assert len(result.items) == 5

        # Verify offset was called with correct value: (3-1) * 5 = 10
        query_mock.order_by.return_value.offset.assert_called_once_with(10)

    @pytest.mark.asyncio
    async def test_list_jobs_parses_tags_json(self, mock_db, mock_job):
        """list_jobs should parse tags_json from TEXT into a list of strings."""
        mock_job.tags_json = '["React", "TypeScript", "Node.js"]'

        query_mock = MagicMock()
        mock_db.query.return_value.filter.return_value = query_mock
        query_mock.count.return_value = 1
        query_mock.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [mock_job]

        result = await list_jobs(page=1, page_size=10, work_mode=None, db=mock_db)

        assert result.items[0].tags == ["React", "TypeScript", "Node.js"]

    @pytest.mark.asyncio
    async def test_list_jobs_handles_null_tags(self, mock_db, mock_job):
        """list_jobs should return empty list for null/missing tags_json."""
        mock_job.tags_json = None

        query_mock = MagicMock()
        mock_db.query.return_value.filter.return_value = query_mock
        query_mock.count.return_value = 1
        query_mock.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [mock_job]

        result = await list_jobs(page=1, page_size=10, work_mode=None, db=mock_db)

        assert result.items[0].tags == []
