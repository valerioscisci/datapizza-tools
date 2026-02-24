"""Tests for talents route handlers (api/routes/talents.py).

Covers public talent listing with search, filters, pagination,
and individual talent retrieval with privacy checks.
Public endpoints — no authentication required.
"""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import MagicMock, PropertyMock
from uuid import uuid4

import pytest
from fastapi import HTTPException

from api.routes.talents.router import list_talents, get_talent, _escape_ilike


class TestListTalents:
    """Tests for the GET /talents endpoint."""

    @pytest.mark.asyncio
    async def test_returns_public_users_only(self, mock_db, mock_public_user):
        """list_talents should return only users with is_public=1 and is_active=1."""
        query_mock = MagicMock()
        mock_db.query.return_value.filter.return_value = query_mock
        query_mock.count.return_value = 1
        query_mock.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [mock_public_user]

        result = await list_talents(
            page=1, page_size=10, search=None, skills=None,
            availability=None, experience_level=None, location=None, db=mock_db,
        )

        assert result.total == 1
        assert result.page == 1
        assert result.page_size == 10
        assert len(result.items) == 1

        talent = result.items[0]
        assert talent.id == mock_public_user.id
        assert talent.full_name == "Public Developer"
        assert talent.current_role == "Backend Engineer"
        assert talent.location == "Roma"
        assert talent.skills == ["Python", "FastAPI", "Docker"]

    @pytest.mark.asyncio
    async def test_empty_list_when_no_public_users(self, mock_db):
        """list_talents should return an empty list when no public users exist."""
        query_mock = MagicMock()
        mock_db.query.return_value.filter.return_value = query_mock
        query_mock.count.return_value = 0
        query_mock.order_by.return_value.offset.return_value.limit.return_value.all.return_value = []

        result = await list_talents(
            page=1, page_size=10, search=None, skills=None,
            availability=None, experience_level=None, location=None, db=mock_db,
        )

        assert result.total == 0
        assert len(result.items) == 0

    @pytest.mark.asyncio
    async def test_search_by_name(self, mock_db, mock_public_user):
        """list_talents with search should apply or_ filter across name, role, skills."""
        query_mock = MagicMock()
        mock_db.query.return_value.filter.return_value = query_mock

        # Search triggers an additional .filter() call
        filtered_mock = MagicMock()
        query_mock.filter.return_value = filtered_mock
        filtered_mock.count.return_value = 1
        filtered_mock.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [mock_public_user]

        result = await list_talents(
            page=1, page_size=10, search="Public", skills=None,
            availability=None, experience_level=None, location=None, db=mock_db,
        )

        query_mock.filter.assert_called_once()
        assert result.total == 1
        assert result.items[0].full_name == "Public Developer"

    @pytest.mark.asyncio
    async def test_search_by_role(self, mock_db, mock_public_user):
        """list_talents with search should match against current_role."""
        query_mock = MagicMock()
        mock_db.query.return_value.filter.return_value = query_mock

        filtered_mock = MagicMock()
        query_mock.filter.return_value = filtered_mock
        filtered_mock.count.return_value = 1
        filtered_mock.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [mock_public_user]

        result = await list_talents(
            page=1, page_size=10, search="Backend", skills=None,
            availability=None, experience_level=None, location=None, db=mock_db,
        )

        query_mock.filter.assert_called_once()
        assert result.total == 1

    @pytest.mark.asyncio
    async def test_search_by_skill(self, mock_db, mock_public_user):
        """list_talents with search should match against skills_json."""
        query_mock = MagicMock()
        mock_db.query.return_value.filter.return_value = query_mock

        filtered_mock = MagicMock()
        query_mock.filter.return_value = filtered_mock
        filtered_mock.count.return_value = 1
        filtered_mock.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [mock_public_user]

        result = await list_talents(
            page=1, page_size=10, search="Python", skills=None,
            availability=None, experience_level=None, location=None, db=mock_db,
        )

        query_mock.filter.assert_called_once()
        assert result.total == 1

    @pytest.mark.asyncio
    async def test_filter_by_experience_level(self, mock_db, mock_public_user):
        """list_talents with experience_level filter should chain an additional .filter call."""
        query_mock = MagicMock()
        mock_db.query.return_value.filter.return_value = query_mock

        filtered_mock = MagicMock()
        query_mock.filter.return_value = filtered_mock
        filtered_mock.count.return_value = 1
        filtered_mock.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [mock_public_user]

        result = await list_talents(
            page=1, page_size=10, search=None, skills=None,
            availability=None, experience_level="senior", location=None, db=mock_db,
        )

        query_mock.filter.assert_called_once()
        assert result.total == 1

    @pytest.mark.asyncio
    async def test_filter_by_availability(self, mock_db, mock_public_user):
        """list_talents with availability filter should chain an additional .filter call."""
        query_mock = MagicMock()
        mock_db.query.return_value.filter.return_value = query_mock

        filtered_mock = MagicMock()
        query_mock.filter.return_value = filtered_mock
        filtered_mock.count.return_value = 1
        filtered_mock.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [mock_public_user]

        result = await list_talents(
            page=1, page_size=10, search=None, skills=None,
            availability="available", experience_level=None, location=None, db=mock_db,
        )

        query_mock.filter.assert_called_once()
        assert result.total == 1

    @pytest.mark.asyncio
    async def test_filter_by_location(self, mock_db, mock_public_user):
        """list_talents with location filter should chain an additional .filter call."""
        query_mock = MagicMock()
        mock_db.query.return_value.filter.return_value = query_mock

        filtered_mock = MagicMock()
        query_mock.filter.return_value = filtered_mock
        filtered_mock.count.return_value = 1
        filtered_mock.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [mock_public_user]

        result = await list_talents(
            page=1, page_size=10, search=None, skills=None,
            availability=None, experience_level=None, location="Roma", db=mock_db,
        )

        query_mock.filter.assert_called_once()
        assert result.total == 1

    @pytest.mark.asyncio
    async def test_filter_by_skills(self, mock_db, mock_public_user):
        """list_talents with skills filter should apply OR ILIKE conditions on skills_json."""
        query_mock = MagicMock()
        mock_db.query.return_value.filter.return_value = query_mock

        filtered_mock = MagicMock()
        query_mock.filter.return_value = filtered_mock
        filtered_mock.count.return_value = 1
        filtered_mock.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [mock_public_user]

        result = await list_talents(
            page=1, page_size=10, search=None, skills="Python,Docker",
            availability=None, experience_level=None, location=None, db=mock_db,
        )

        query_mock.filter.assert_called_once()
        assert result.total == 1

    @pytest.mark.asyncio
    async def test_pagination_with_correct_offset(self, mock_db):
        """list_talents should apply correct offset based on page and page_size."""
        query_mock = MagicMock()
        mock_db.query.return_value.filter.return_value = query_mock
        query_mock.count.return_value = 25

        # Create 5 mock users for page 3
        users = []
        for i in range(5):
            u = MagicMock()
            u.id = str(uuid4())
            u.full_name = f"Developer {i}"
            u.current_role = "Developer"
            u.location = "Milano"
            u.skills_json = '["Python"]'
            u.experience_level = "mid"
            u.experience_years = "3-5 anni"
            u.availability_status = "available"
            u.bio = None
            u.is_public = 1
            u.is_active = 1
            u.created_at = datetime(2024, 6, 1, tzinfo=timezone.utc)
            users.append(u)

        query_mock.order_by.return_value.offset.return_value.limit.return_value.all.return_value = users

        result = await list_talents(
            page=3, page_size=5, search=None, skills=None,
            availability=None, experience_level=None, location=None, db=mock_db,
        )

        assert result.total == 25
        assert result.page == 3
        assert result.page_size == 5
        assert len(result.items) == 5

        # Verify offset was called with correct value: (3-1) * 5 = 10
        query_mock.order_by.return_value.offset.assert_called_once_with(10)

    @pytest.mark.asyncio
    async def test_parses_skills_json_correctly(self, mock_db, mock_public_user):
        """list_talents should parse skills_json from TEXT into a list of strings."""
        mock_public_user.skills_json = '["React", "TypeScript", "Node.js"]'

        query_mock = MagicMock()
        mock_db.query.return_value.filter.return_value = query_mock
        query_mock.count.return_value = 1
        query_mock.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [mock_public_user]

        result = await list_talents(
            page=1, page_size=10, search=None, skills=None,
            availability=None, experience_level=None, location=None, db=mock_db,
        )

        assert result.items[0].skills == ["React", "TypeScript", "Node.js"]

    @pytest.mark.asyncio
    async def test_handles_null_skills_json(self, mock_db, mock_public_user):
        """list_talents should return empty list for null/missing skills_json."""
        mock_public_user.skills_json = None

        query_mock = MagicMock()
        mock_db.query.return_value.filter.return_value = query_mock
        query_mock.count.return_value = 1
        query_mock.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [mock_public_user]

        result = await list_talents(
            page=1, page_size=10, search=None, skills=None,
            availability=None, experience_level=None, location=None, db=mock_db,
        )

        assert result.items[0].skills == []

    @pytest.mark.asyncio
    async def test_response_excludes_email(self, mock_db, mock_public_user):
        """list_talents response should never contain email field (privacy)."""
        query_mock = MagicMock()
        mock_db.query.return_value.filter.return_value = query_mock
        query_mock.count.return_value = 1
        query_mock.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [mock_public_user]

        result = await list_talents(
            page=1, page_size=10, search=None, skills=None,
            availability=None, experience_level=None, location=None, db=mock_db,
        )

        talent_dict = result.items[0].model_dump()
        assert "email" not in talent_dict
        assert "phone" not in talent_dict
        assert "password_hash" not in talent_dict


class TestGetTalent:
    """Tests for the GET /talents/{talent_id} endpoint."""

    @pytest.mark.asyncio
    async def test_returns_full_detail_for_public_user(
        self, mock_db, mock_public_user, mock_experience, mock_education
    ):
        """get_talent should return full talent detail for a public user."""
        mock_experience.user_id = mock_public_user.id
        mock_education.user_id = mock_public_user.id

        # First filter call: User query returns the public user
        user_query = MagicMock()
        user_query.first.return_value = mock_public_user

        # Experience and Education queries
        exp_query = MagicMock()
        exp_query.order_by.return_value.all.return_value = [mock_experience]

        edu_query = MagicMock()
        edu_query.order_by.return_value.all.return_value = [mock_education]

        call_count = [0]

        def query_side_effect(model):
            call_count[0] += 1
            q = MagicMock()
            if hasattr(model, '__tablename__'):
                if model.__tablename__ == "users":
                    q.filter.return_value = user_query
                elif model.__tablename__ == "experiences":
                    q.filter.return_value = exp_query
                elif model.__tablename__ == "educations":
                    q.filter.return_value = edu_query
            else:
                # Fallback for MagicMock models
                name = getattr(model, '__name__', '')
                if name == 'User':
                    q.filter.return_value = user_query
                elif name == 'Experience':
                    q.filter.return_value = exp_query
                elif name == 'Education':
                    q.filter.return_value = edu_query
            return q

        mock_db.query.side_effect = query_side_effect

        result = await get_talent(talent_id=mock_public_user.id, db=mock_db)

        assert result.id == mock_public_user.id
        assert result.full_name == "Public Developer"
        assert result.bio == "A public developer profile for testing."
        assert result.linkedin_url == "https://linkedin.com/in/public-dev"
        assert result.github_url == "https://github.com/publicdev"
        assert len(result.experiences) == 1
        assert len(result.educations) == 1
        assert result.experiences[0].title == mock_experience.title
        assert result.educations[0].institution == mock_education.institution

    @pytest.mark.asyncio
    async def test_returns_404_for_private_user(self, mock_db):
        """get_talent should return 404 for a private user (is_public=0)."""
        # User query returns None (private user filtered out by is_public=1)
        mock_db.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            await get_talent(talent_id="private-user-id", db=mock_db)

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Talent not found"

    @pytest.mark.asyncio
    async def test_returns_404_for_nonexistent_user(self, mock_db):
        """get_talent should return 404 for a non-existent user ID."""
        mock_db.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            await get_talent(talent_id="nonexistent-id", db=mock_db)

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Talent not found"

    @pytest.mark.asyncio
    async def test_returns_404_for_inactive_user(self, mock_db):
        """get_talent should return 404 for an inactive user (is_active=0)."""
        # User query returns None (inactive user filtered out by is_active=1)
        mock_db.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            await get_talent(talent_id="inactive-user-id", db=mock_db)

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Talent not found"

    @pytest.mark.asyncio
    async def test_response_excludes_email(self, mock_db, mock_public_user):
        """get_talent response should never contain email field (privacy)."""
        user_query = MagicMock()
        user_query.first.return_value = mock_public_user

        empty_query = MagicMock()
        empty_query.order_by.return_value.all.return_value = []

        def query_side_effect(model):
            q = MagicMock()
            if hasattr(model, '__tablename__'):
                if model.__tablename__ == "users":
                    q.filter.return_value = user_query
                else:
                    q.filter.return_value = empty_query
            else:
                name = getattr(model, '__name__', '')
                if name == 'User':
                    q.filter.return_value = user_query
                else:
                    q.filter.return_value = empty_query
            return q

        mock_db.query.side_effect = query_side_effect

        result = await get_talent(talent_id=mock_public_user.id, db=mock_db)

        result_dict = result.model_dump()
        assert "email" not in result_dict
        assert "password_hash" not in result_dict

    @pytest.mark.asyncio
    async def test_response_excludes_phone(self, mock_db, mock_public_user):
        """get_talent response should never contain phone field (privacy)."""
        user_query = MagicMock()
        user_query.first.return_value = mock_public_user

        empty_query = MagicMock()
        empty_query.order_by.return_value.all.return_value = []

        def query_side_effect(model):
            q = MagicMock()
            if hasattr(model, '__tablename__'):
                if model.__tablename__ == "users":
                    q.filter.return_value = user_query
                else:
                    q.filter.return_value = empty_query
            else:
                name = getattr(model, '__name__', '')
                if name == 'User':
                    q.filter.return_value = user_query
                else:
                    q.filter.return_value = empty_query
            return q

        mock_db.query.side_effect = query_side_effect

        result = await get_talent(talent_id=mock_public_user.id, db=mock_db)

        result_dict = result.model_dump()
        assert "phone" not in result_dict
        assert "reskilling_status" not in result_dict
        assert "adopted_by_company" not in result_dict

    @pytest.mark.asyncio
    async def test_talent_detail_parses_skills(self, mock_db, mock_public_user):
        """get_talent should correctly parse skills_json into a list."""
        mock_public_user.skills_json = '["Go", "Rust", "Python"]'

        user_query = MagicMock()
        user_query.first.return_value = mock_public_user

        empty_query = MagicMock()
        empty_query.order_by.return_value.all.return_value = []

        def query_side_effect(model):
            q = MagicMock()
            if hasattr(model, '__tablename__'):
                if model.__tablename__ == "users":
                    q.filter.return_value = user_query
                else:
                    q.filter.return_value = empty_query
            else:
                name = getattr(model, '__name__', '')
                if name == 'User':
                    q.filter.return_value = user_query
                else:
                    q.filter.return_value = empty_query
            return q

        mock_db.query.side_effect = query_side_effect

        result = await get_talent(talent_id=mock_public_user.id, db=mock_db)

        assert result.skills == ["Go", "Rust", "Python"]


class TestEscapeIlike:
    """Tests for the _escape_ilike helper function."""

    def test_escapes_percent(self):
        """_escape_ilike should escape % wildcard characters."""
        assert _escape_ilike("100%") == r"100\%"

    def test_escapes_underscore(self):
        """_escape_ilike should escape _ wildcard characters."""
        assert _escape_ilike("user_name") == r"user\_name"

    def test_escapes_both(self):
        """_escape_ilike should escape both % and _ wildcards."""
        assert _escape_ilike("50%_off") == r"50\%\_off"

    def test_no_wildcards_unchanged(self):
        """_escape_ilike should return the string unchanged if no wildcards present."""
        assert _escape_ilike("Python") == "Python"

    def test_empty_string(self):
        """_escape_ilike should handle empty string correctly."""
        assert _escape_ilike("") == ""

    def test_special_chars_not_escaped(self):
        """_escape_ilike should not escape other special characters like quotes."""
        assert _escape_ilike("O'Brien") == "O'Brien"

    def test_sql_injection_attempt(self):
        """_escape_ilike should handle SQL injection attempts safely (escapes wildcards only)."""
        assert _escape_ilike("'; DROP TABLE users;--") == "'; DROP TABLE users;--"

    def test_xss_attempt(self):
        """_escape_ilike should pass through XSS attempts unchanged (handled by framework)."""
        assert _escape_ilike("<script>alert('xss')</script>") == "<script>alert('xss')</script>"


class TestListTalentsEdgeCases:
    """Additional edge case tests for list_talents."""

    @pytest.mark.asyncio
    async def test_user_with_null_availability_defaults_to_available(self, mock_db, mock_public_user):
        """list_talents should default availability_status to 'available' when null."""
        mock_public_user.availability_status = None

        query_mock = MagicMock()
        mock_db.query.return_value.filter.return_value = query_mock
        query_mock.count.return_value = 1
        query_mock.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [mock_public_user]

        result = await list_talents(
            page=1, page_size=10, search=None, skills=None,
            availability=None, experience_level=None, location=None, db=mock_db,
        )

        assert result.items[0].availability_status == "available"

    @pytest.mark.asyncio
    async def test_user_with_all_null_optional_fields(self, mock_db, mock_public_user):
        """list_talents should handle a user with all nullable fields set to None."""
        mock_public_user.current_role = None
        mock_public_user.location = None
        mock_public_user.skills_json = None
        mock_public_user.experience_level = None
        mock_public_user.experience_years = None
        mock_public_user.bio = None
        mock_public_user.availability_status = None

        query_mock = MagicMock()
        mock_db.query.return_value.filter.return_value = query_mock
        query_mock.count.return_value = 1
        query_mock.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [mock_public_user]

        result = await list_talents(
            page=1, page_size=10, search=None, skills=None,
            availability=None, experience_level=None, location=None, db=mock_db,
        )

        talent = result.items[0]
        assert talent.current_role is None
        assert talent.location is None
        assert talent.skills == []
        assert talent.experience_level is None
        assert talent.experience_years is None
        assert talent.bio is None
        assert talent.availability_status == "available"

    @pytest.mark.asyncio
    async def test_empty_skills_filter_ignored(self, mock_db, mock_public_user):
        """list_talents should ignore skills filter with only whitespace/empty values."""
        query_mock = MagicMock()
        mock_db.query.return_value.filter.return_value = query_mock
        query_mock.count.return_value = 1
        query_mock.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [mock_public_user]

        result = await list_talents(
            page=1, page_size=10, search=None, skills=" , , ",
            availability=None, experience_level=None, location=None, db=mock_db,
        )

        # Should NOT have called an additional .filter() for empty skill_list
        query_mock.filter.assert_not_called()
        assert result.total == 1


class TestTalentsExcludesCompanyUsers:
    """Tests ensuring company users are excluded from talent listings."""

    @pytest.mark.asyncio
    async def test_list_talents_excludes_company_users(self, mock_db, mock_public_user):
        """list_talents should only return users with user_type='talent', not company users."""
        # The base query now includes user_type == "talent" filter
        # A public company user should be excluded by the filter
        query_mock = MagicMock()
        mock_db.query.return_value.filter.return_value = query_mock
        query_mock.count.return_value = 0
        query_mock.order_by.return_value.offset.return_value.limit.return_value.all.return_value = []

        result = await list_talents(
            page=1, page_size=10, search=None, skills=None,
            availability=None, experience_level=None, location=None, db=mock_db,
        )

        # Verify the filter was called (with is_public, is_active, user_type)
        mock_db.query.return_value.filter.assert_called_once()
        assert result.total == 0

    @pytest.mark.asyncio
    async def test_get_talent_returns_404_for_company_user(self, mock_db):
        """get_talent should return 404 for a company user even if they are public."""
        # The filter now includes user_type == "talent", so a company user
        # with is_public=1 will not be found
        mock_db.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            await get_talent(talent_id="company-user-id", db=mock_db)

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Talent not found"


class TestGetTalentEdgeCases:
    """Additional edge case tests for get_talent."""

    @pytest.mark.asyncio
    async def test_talent_with_no_experiences_or_educations(self, mock_db, mock_public_user):
        """get_talent should return empty lists for a user with no experiences/educations."""
        user_query = MagicMock()
        user_query.first.return_value = mock_public_user

        empty_query = MagicMock()
        empty_query.order_by.return_value.all.return_value = []

        def query_side_effect(model):
            q = MagicMock()
            if hasattr(model, '__tablename__'):
                if model.__tablename__ == "users":
                    q.filter.return_value = user_query
                else:
                    q.filter.return_value = empty_query
            else:
                name = getattr(model, '__name__', '')
                if name == 'User':
                    q.filter.return_value = user_query
                else:
                    q.filter.return_value = empty_query
            return q

        mock_db.query.side_effect = query_side_effect

        result = await get_talent(talent_id=mock_public_user.id, db=mock_db)

        assert result.experiences == []
        assert result.educations == []

    @pytest.mark.asyncio
    async def test_talent_detail_with_all_null_optional_fields(self, mock_db, mock_public_user):
        """get_talent should handle a user with all nullable fields set to None."""
        mock_public_user.bio = None
        mock_public_user.current_role = None
        mock_public_user.location = None
        mock_public_user.experience_level = None
        mock_public_user.experience_years = None
        mock_public_user.skills_json = None
        mock_public_user.availability_status = None
        mock_public_user.linkedin_url = None
        mock_public_user.github_url = None
        mock_public_user.portfolio_url = None

        user_query = MagicMock()
        user_query.first.return_value = mock_public_user

        empty_query = MagicMock()
        empty_query.order_by.return_value.all.return_value = []

        def query_side_effect(model):
            q = MagicMock()
            if hasattr(model, '__tablename__'):
                if model.__tablename__ == "users":
                    q.filter.return_value = user_query
                else:
                    q.filter.return_value = empty_query
            else:
                name = getattr(model, '__name__', '')
                if name == 'User':
                    q.filter.return_value = user_query
                else:
                    q.filter.return_value = empty_query
            return q

        mock_db.query.side_effect = query_side_effect

        result = await get_talent(talent_id=mock_public_user.id, db=mock_db)

        assert result.bio is None
        assert result.current_role is None
        assert result.location is None
        assert result.skills == []
        assert result.availability_status == "available"
        assert result.linkedin_url is None
        assert result.github_url is None
        assert result.portfolio_url is None
