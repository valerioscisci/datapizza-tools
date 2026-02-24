"""Tests for news route handlers (api/routes/news.py).

Covers news listing with pagination and category filtering,
and individual news retrieval by ID.
"""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from fastapi import HTTPException

from api.routes.news.router import list_news, get_news, _to_news_response


class TestToNewsResponse:
    """Tests for the _to_news_response helper function."""

    def test_converts_news_to_response(self, mock_news):
        """_to_news_response should convert a News model to a NewsResponse with parsed tags."""
        result = _to_news_response(mock_news)
        assert result.id == mock_news.id
        assert result.title == "AI Trends 2024"
        assert result.source == "Hacker News"
        assert result.category == "AI"
        assert result.tags == ["AI", "Machine Learning"]

    def test_handles_null_tags(self, mock_news):
        """_to_news_response should return empty tags list when tags_json is None."""
        mock_news.tags_json = None
        result = _to_news_response(mock_news)
        assert result.tags == []


class TestListNews:
    """Tests for the GET /news endpoint."""

    @pytest.mark.asyncio
    async def test_list_news_returns_items(self, mock_db, mock_news):
        """list_news should return news items with parsed tags and pagination info."""
        query_mock = MagicMock()
        mock_db.query.return_value.filter.return_value = query_mock
        query_mock.count.return_value = 1
        query_mock.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [mock_news]

        result = await list_news(page=1, page_size=10, category=None, db=mock_db)

        assert result.total == 1
        assert result.page == 1
        assert result.page_size == 10
        assert len(result.items) == 1
        assert result.items[0].title == "AI Trends 2024"
        assert result.items[0].tags == ["AI", "Machine Learning"]

    @pytest.mark.asyncio
    async def test_list_news_empty(self, mock_db):
        """list_news should return an empty list when no news exist."""
        query_mock = MagicMock()
        mock_db.query.return_value.filter.return_value = query_mock
        query_mock.count.return_value = 0
        query_mock.order_by.return_value.offset.return_value.limit.return_value.all.return_value = []

        result = await list_news(page=1, page_size=10, category=None, db=mock_db)

        assert result.total == 0
        assert len(result.items) == 0

    @pytest.mark.asyncio
    async def test_list_news_with_category_filter(self, mock_db, mock_news):
        """list_news with category filter should apply an additional .filter call."""
        query_mock = MagicMock()
        mock_db.query.return_value.filter.return_value = query_mock

        filtered_mock = MagicMock()
        query_mock.filter.return_value = filtered_mock
        filtered_mock.count.return_value = 1
        filtered_mock.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [mock_news]

        result = await list_news(page=1, page_size=10, category="AI", db=mock_db)

        query_mock.filter.assert_called_once()
        assert result.total == 1
        assert result.items[0].category == "AI"

    @pytest.mark.asyncio
    async def test_list_news_pagination(self, mock_db, mock_news):
        """list_news should apply correct offset based on page and page_size."""
        query_mock = MagicMock()
        mock_db.query.return_value.filter.return_value = query_mock
        query_mock.count.return_value = 20
        query_mock.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [mock_news]

        result = await list_news(page=2, page_size=5, category=None, db=mock_db)

        assert result.total == 20
        assert result.page == 2
        assert result.page_size == 5
        # Verify offset: (2-1) * 5 = 5
        query_mock.order_by.return_value.offset.assert_called_once_with(5)


class TestGetNews:
    """Tests for the GET /news/{news_id} endpoint."""

    @pytest.mark.asyncio
    async def test_get_news_returns_news_by_id(self, mock_db, mock_news):
        """get_news should return a single news item when found."""
        mock_db.query.return_value.filter.return_value.first.return_value = mock_news

        result = await get_news(news_id=mock_news.id, db=mock_db)

        assert result.id == mock_news.id
        assert result.title == "AI Trends 2024"

    @pytest.mark.asyncio
    async def test_get_news_nonexistent_returns_404(self, mock_db):
        """get_news with a non-existent ID should raise HTTP 404."""
        mock_db.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            await get_news(news_id="nonexistent-id", db=mock_db)
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "News not found"
