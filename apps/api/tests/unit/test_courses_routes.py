"""Tests for courses route handlers (api/routes/courses.py).

Covers course listing with pagination, category and level filtering,
and individual course retrieval by ID.
"""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from fastapi import HTTPException

from api.routes.courses import list_courses, get_course, _to_course_response


class TestToCourseResponse:
    """Tests for the _to_course_response helper function."""

    def test_converts_course_to_response(self, mock_course):
        """_to_course_response should convert a Course model to a CourseResponse with parsed tags."""
        result = _to_course_response(mock_course)
        assert result.id == mock_course.id
        assert result.title == "Machine Learning with Python"
        assert result.provider == "Coursera"
        assert result.level == "intermediate"
        assert result.tags == ["Python", "Machine Learning", "TensorFlow"]

    def test_handles_null_tags(self, mock_course):
        """_to_course_response should return empty tags list when tags_json is None."""
        mock_course.tags_json = None
        result = _to_course_response(mock_course)
        assert result.tags == []


class TestListCourses:
    """Tests for the GET /courses endpoint."""

    @pytest.mark.asyncio
    async def test_list_courses_returns_items(self, mock_db, mock_course):
        """list_courses should return course items with parsed tags and pagination info."""
        query_mock = MagicMock()
        mock_db.query.return_value.filter.return_value = query_mock
        query_mock.count.return_value = 1
        query_mock.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [mock_course]

        result = await list_courses(
            page=1, page_size=10, category=None, level=None, db=mock_db
        )

        assert result.total == 1
        assert result.page == 1
        assert result.page_size == 10
        assert len(result.items) == 1
        assert result.items[0].title == "Machine Learning with Python"
        assert result.items[0].tags == ["Python", "Machine Learning", "TensorFlow"]

    @pytest.mark.asyncio
    async def test_list_courses_empty(self, mock_db):
        """list_courses should return an empty list when no courses exist."""
        query_mock = MagicMock()
        mock_db.query.return_value.filter.return_value = query_mock
        query_mock.count.return_value = 0
        query_mock.order_by.return_value.offset.return_value.limit.return_value.all.return_value = []

        result = await list_courses(
            page=1, page_size=10, category=None, level=None, db=mock_db
        )

        assert result.total == 0
        assert len(result.items) == 0

    @pytest.mark.asyncio
    async def test_list_courses_with_category_filter(self, mock_db, mock_course):
        """list_courses with category filter should apply an additional .filter call."""
        query_mock = MagicMock()
        mock_db.query.return_value.filter.return_value = query_mock

        filtered_mock = MagicMock()
        query_mock.filter.return_value = filtered_mock
        filtered_mock.count.return_value = 1
        filtered_mock.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [mock_course]

        result = await list_courses(
            page=1, page_size=10, category="ML", level=None, db=mock_db
        )

        query_mock.filter.assert_called_once()
        assert result.total == 1

    @pytest.mark.asyncio
    async def test_list_courses_with_level_filter(self, mock_db, mock_course):
        """list_courses with level filter should apply an additional .filter call."""
        query_mock = MagicMock()
        mock_db.query.return_value.filter.return_value = query_mock

        filtered_mock = MagicMock()
        query_mock.filter.return_value = filtered_mock
        filtered_mock.count.return_value = 1
        filtered_mock.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [mock_course]

        result = await list_courses(
            page=1, page_size=10, category=None, level="intermediate", db=mock_db
        )

        query_mock.filter.assert_called_once()
        assert result.total == 1

    @pytest.mark.asyncio
    async def test_list_courses_with_both_filters(self, mock_db, mock_course):
        """list_courses with both category and level filters should chain two .filter calls."""
        query_mock = MagicMock()
        mock_db.query.return_value.filter.return_value = query_mock

        # First filter (category)
        filtered_1 = MagicMock()
        query_mock.filter.return_value = filtered_1

        # Second filter (level)
        filtered_2 = MagicMock()
        filtered_1.filter.return_value = filtered_2
        filtered_2.count.return_value = 1
        filtered_2.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [mock_course]

        result = await list_courses(
            page=1, page_size=10, category="ML", level="intermediate", db=mock_db
        )

        query_mock.filter.assert_called_once()  # category filter
        filtered_1.filter.assert_called_once()  # level filter
        assert result.total == 1

    @pytest.mark.asyncio
    async def test_list_courses_pagination(self, mock_db, mock_course):
        """list_courses should apply correct offset based on page and page_size."""
        query_mock = MagicMock()
        mock_db.query.return_value.filter.return_value = query_mock
        query_mock.count.return_value = 30
        query_mock.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [mock_course]

        result = await list_courses(
            page=3, page_size=10, category=None, level=None, db=mock_db
        )

        assert result.total == 30
        assert result.page == 3
        assert result.page_size == 10
        # Verify offset: (3-1) * 10 = 20
        query_mock.order_by.return_value.offset.assert_called_once_with(20)


class TestGetCourse:
    """Tests for the GET /courses/{course_id} endpoint."""

    @pytest.mark.asyncio
    async def test_get_course_returns_course_by_id(self, mock_db, mock_course):
        """get_course should return a single course when found."""
        mock_db.query.return_value.filter.return_value.first.return_value = mock_course

        result = await get_course(course_id=mock_course.id, db=mock_db)

        assert result.id == mock_course.id
        assert result.title == "Machine Learning with Python"
        assert result.provider == "Coursera"

    @pytest.mark.asyncio
    async def test_get_course_nonexistent_returns_404(self, mock_db):
        """get_course with a non-existent ID should raise HTTP 404."""
        mock_db.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            await get_course(course_id="nonexistent-id", db=mock_db)
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Course not found"
