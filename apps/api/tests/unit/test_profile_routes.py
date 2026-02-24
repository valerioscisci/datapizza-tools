"""Tests for profile route handlers (api/routes/profile.py).

Covers profile retrieval with experiences and educations,
profile updates (including skills JSON conversion), and
full CRUD for experiences and educations with ownership checks.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch, call
from uuid import uuid4

import pytest
from fastapi import HTTPException

from api.routes.profile import (
    get_profile,
    update_profile,
    create_experience,
    update_experience,
    delete_experience,
    create_education,
    update_education,
    delete_education,
    _experience_to_response,
    _education_to_response,
    _build_profile_response,
)
from api.schemas.profile import ProfileUpdate
from api.schemas.experience import ExperienceCreate, ExperienceUpdate
from api.schemas.education import EducationCreate, EducationUpdate


class TestHelperFunctions:
    """Tests for response-building helper functions."""

    def test_experience_to_response(self, mock_experience):
        """_experience_to_response should convert Experience model to ExperienceResponse."""
        result = _experience_to_response(mock_experience)
        assert result.id == mock_experience.id
        assert result.title == "Frontend Developer"
        assert result.company == "StartupXYZ"
        assert result.is_current is True  # SQLite integer 1 -> bool True

    def test_education_to_response(self, mock_education):
        """_education_to_response should convert Education model to EducationResponse."""
        result = _education_to_response(mock_education)
        assert result.id == mock_education.id
        assert result.institution == "Politecnico di Milano"
        assert result.degree_type == "master"
        assert result.is_current is False  # SQLite integer 0 -> bool False

    def test_build_profile_response(self, mock_user, mock_experience, mock_education):
        """_build_profile_response should assemble a complete ProfileResponse."""
        result = _build_profile_response(mock_user, [mock_experience], [mock_education])
        assert result.id == mock_user.id
        assert result.email == mock_user.email
        assert result.skills == ["Python", "FastAPI"]
        assert len(result.experiences) == 1
        assert len(result.educations) == 1
        assert result.experiences[0].title == "Frontend Developer"
        assert result.educations[0].institution == "Politecnico di Milano"


class TestGetProfile:
    """Tests for the GET /profile endpoint."""

    @pytest.mark.asyncio
    async def test_returns_profile_with_experiences_and_educations(
        self, mock_db, mock_user, mock_experience, mock_education
    ):
        """get_profile should return the user's profile with their experiences and educations."""
        mock_experience.user_id = mock_user.id
        mock_education.user_id = mock_user.id

        # Set up two different filter chains for Experience and Education queries
        exp_query = MagicMock()
        exp_query.order_by.return_value.all.return_value = [mock_experience]

        edu_query = MagicMock()
        edu_query.order_by.return_value.all.return_value = [mock_education]

        # mock_db.query(Experience).filter(...) and mock_db.query(Education).filter(...)
        def query_side_effect(model):
            q = MagicMock()
            if model.__name__ == "Experience":
                q.filter.return_value = exp_query
            elif model.__name__ == "Education":
                q.filter.return_value = edu_query
            return q

        mock_db.query.side_effect = query_side_effect

        # We need to patch the model classes so __name__ works
        from api.database.models import Experience, Education

        result = await get_profile(current_user=mock_user, db=mock_db)

        assert result.id == mock_user.id
        assert result.full_name == mock_user.full_name
        assert len(result.experiences) == 1
        assert len(result.educations) == 1

    @pytest.mark.asyncio
    async def test_returns_empty_lists_when_no_experiences_or_educations(
        self, mock_db, mock_user
    ):
        """get_profile should return empty experience and education lists when none exist."""
        empty_query = MagicMock()
        empty_query.order_by.return_value.all.return_value = []

        mock_db.query.return_value.filter.return_value = empty_query

        result = await get_profile(current_user=mock_user, db=mock_db)

        assert result.id == mock_user.id
        assert result.experiences == []
        assert result.educations == []


class TestUpdateProfile:
    """Tests for the PATCH /profile endpoint."""

    @pytest.mark.asyncio
    async def test_update_profile_fields(self, mock_db, mock_user):
        """update_profile should update the specified fields on the user model."""
        data = ProfileUpdate(bio="Updated bio", location="Roma")

        empty_query = MagicMock()
        empty_query.order_by.return_value.all.return_value = []
        mock_db.query.return_value.filter.return_value = empty_query

        result = await update_profile(data=data, current_user=mock_user, db=mock_db)

        assert mock_user.bio == "Updated bio"
        assert mock_user.location == "Roma"
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once_with(mock_user)

    @pytest.mark.asyncio
    async def test_update_skills_json_conversion(self, mock_db, mock_user):
        """update_profile with skills should convert list to JSON string in skills_json."""
        data = ProfileUpdate(skills=["React", "Vue", "Angular"])

        empty_query = MagicMock()
        empty_query.order_by.return_value.all.return_value = []
        mock_db.query.return_value.filter.return_value = empty_query

        result = await update_profile(data=data, current_user=mock_user, db=mock_db)

        assert mock_user.skills_json == '["React", "Vue", "Angular"]'

    @pytest.mark.asyncio
    async def test_update_skills_none_sets_empty_array(self, mock_db, mock_user):
        """update_profile with skills=None should set skills_json to '[]'."""
        data = ProfileUpdate(skills=None)

        # We need to ensure skills is explicitly set (not just missing)
        # Force it into the model_dump
        update_data = data.model_dump(exclude_unset=True)
        # Since skills=None is explicitly passed, it should appear in exclude_unset
        # Actually, Pydantic treats explicitly passed None as "set"
        # Let's test the actual behavior

        empty_query = MagicMock()
        empty_query.order_by.return_value.all.return_value = []
        mock_db.query.return_value.filter.return_value = empty_query

        result = await update_profile(data=data, current_user=mock_user, db=mock_db)

        assert mock_user.skills_json == "[]"

    @pytest.mark.asyncio
    async def test_update_only_provided_fields(self, mock_db, mock_user):
        """update_profile should only update fields that were explicitly provided."""
        original_bio = mock_user.bio
        data = ProfileUpdate(location="Torino")

        empty_query = MagicMock()
        empty_query.order_by.return_value.all.return_value = []
        mock_db.query.return_value.filter.return_value = empty_query

        result = await update_profile(data=data, current_user=mock_user, db=mock_db)

        # bio should remain unchanged
        assert mock_user.bio == original_bio
        assert mock_user.location == "Torino"

    @pytest.mark.asyncio
    async def test_update_is_public_to_true(self, mock_db, mock_user):
        """update_profile with is_public=True should set is_public to 1 (SQLite integer)."""
        mock_user.is_public = 0
        data = ProfileUpdate(is_public=True)

        empty_query = MagicMock()
        empty_query.order_by.return_value.all.return_value = []
        mock_db.query.return_value.filter.return_value = empty_query

        result = await update_profile(data=data, current_user=mock_user, db=mock_db)

        assert mock_user.is_public == 1
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_is_public_to_false(self, mock_db, mock_user):
        """update_profile with is_public=False should set is_public to 0 (SQLite integer)."""
        mock_user.is_public = 1
        data = ProfileUpdate(is_public=False)

        empty_query = MagicMock()
        empty_query.order_by.return_value.all.return_value = []
        mock_db.query.return_value.filter.return_value = empty_query

        result = await update_profile(data=data, current_user=mock_user, db=mock_db)

        assert mock_user.is_public == 0
        mock_db.commit.assert_called_once()


class TestExperienceCRUD:
    """Tests for experience CRUD endpoints (POST, PATCH, DELETE)."""

    @pytest.mark.asyncio
    async def test_create_experience(self, mock_db, mock_user):
        """create_experience should add a new Experience record for the authenticated user."""
        data = ExperienceCreate(
            title="Backend Developer",
            company="BigCorp",
            employment_type="full-time",
            location="Milano",
            start_month=1,
            start_year=2022,
            is_current=True,
            description="Building APIs.",
        )

        def mock_refresh(exp):
            exp.id = str(uuid4())
            exp.created_at = datetime(2024, 1, 1, tzinfo=timezone.utc)

        mock_db.refresh.side_effect = mock_refresh

        result = await create_experience(data=data, current_user=mock_user, db=mock_db)

        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()

        # Verify the Experience object was created with correct values
        added_exp = mock_db.add.call_args[0][0]
        assert added_exp.user_id == mock_user.id
        assert added_exp.title == "Backend Developer"
        assert added_exp.company == "BigCorp"
        assert added_exp.is_current == 1  # SQLite boolean
        assert added_exp.end_month is None  # Cleared because is_current=True
        assert added_exp.end_year is None

    @pytest.mark.asyncio
    async def test_create_experience_not_current(self, mock_db, mock_user):
        """create_experience with is_current=False should preserve end dates."""
        data = ExperienceCreate(
            title="Intern",
            company="StartupABC",
            start_year=2020,
            end_month=12,
            end_year=2021,
            is_current=False,
        )

        def mock_refresh(exp):
            exp.id = str(uuid4())
            exp.created_at = datetime(2024, 1, 1, tzinfo=timezone.utc)

        mock_db.refresh.side_effect = mock_refresh

        result = await create_experience(data=data, current_user=mock_user, db=mock_db)

        added_exp = mock_db.add.call_args[0][0]
        assert added_exp.is_current == 0
        assert added_exp.end_month == 12
        assert added_exp.end_year == 2021

    @pytest.mark.asyncio
    async def test_update_experience(self, mock_db, mock_user, mock_experience):
        """update_experience should modify the specified experience's fields."""
        mock_experience.user_id = mock_user.id
        mock_db.query.return_value.filter.return_value.first.return_value = mock_experience

        data = ExperienceUpdate(title="Senior Frontend Developer")

        result = await update_experience(
            experience_id=mock_experience.id,
            data=data,
            current_user=mock_user,
            db=mock_db,
        )

        assert mock_experience.title == "Senior Frontend Developer"
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_experience_set_current_clears_end_dates(
        self, mock_db, mock_user, mock_experience
    ):
        """Setting is_current=True in update should clear end_month and end_year."""
        mock_experience.user_id = mock_user.id
        mock_experience.end_month = 6
        mock_experience.end_year = 2023
        mock_db.query.return_value.filter.return_value.first.return_value = mock_experience

        data = ExperienceUpdate(is_current=True)

        result = await update_experience(
            experience_id=mock_experience.id,
            data=data,
            current_user=mock_user,
            db=mock_db,
        )

        assert mock_experience.is_current == 1
        assert mock_experience.end_month is None
        assert mock_experience.end_year is None

    @pytest.mark.asyncio
    async def test_delete_experience(self, mock_db, mock_user, mock_experience):
        """delete_experience should remove the experience from the database."""
        mock_experience.user_id = mock_user.id
        mock_db.query.return_value.filter.return_value.first.return_value = mock_experience

        await delete_experience(
            experience_id=mock_experience.id,
            current_user=mock_user,
            db=mock_db,
        )

        mock_db.delete.assert_called_once_with(mock_experience)
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_cannot_modify_other_users_experience(self, mock_db, mock_user):
        """Updating/deleting another user's experience should raise 404."""
        # Experience not found for this user (ownership check fails)
        mock_db.query.return_value.filter.return_value.first.return_value = None

        data = ExperienceUpdate(title="Hacked Title")

        with pytest.raises(HTTPException) as exc_info:
            await update_experience(
                experience_id="other-exp-id",
                data=data,
                current_user=mock_user,
                db=mock_db,
            )
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Experience not found"

    @pytest.mark.asyncio
    async def test_cannot_delete_other_users_experience(self, mock_db, mock_user):
        """Deleting another user's experience should raise 404."""
        mock_db.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            await delete_experience(
                experience_id="other-exp-id",
                current_user=mock_user,
                db=mock_db,
            )
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Experience not found"


class TestEducationCRUD:
    """Tests for education CRUD endpoints (POST, PATCH, DELETE)."""

    @pytest.mark.asyncio
    async def test_create_education(self, mock_db, mock_user):
        """create_education should add a new Education record for the authenticated user."""
        data = EducationCreate(
            institution="Universita' di Bologna",
            degree="Laurea Triennale",
            degree_type="bachelor",
            field_of_study="Informatica",
            start_year=2015,
            end_year=2018,
            is_current=False,
        )

        def mock_refresh(edu):
            edu.id = str(uuid4())
            edu.created_at = datetime(2024, 1, 1, tzinfo=timezone.utc)

        mock_db.refresh.side_effect = mock_refresh

        result = await create_education(data=data, current_user=mock_user, db=mock_db)

        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()

        added_edu = mock_db.add.call_args[0][0]
        assert added_edu.user_id == mock_user.id
        assert added_edu.institution == "Universita' di Bologna"
        assert added_edu.is_current == 0
        assert added_edu.end_year == 2018

    @pytest.mark.asyncio
    async def test_create_education_current(self, mock_db, mock_user):
        """create_education with is_current=True should clear end_year."""
        data = EducationCreate(
            institution="MIT",
            start_year=2023,
            is_current=True,
        )

        def mock_refresh(edu):
            edu.id = str(uuid4())
            edu.created_at = datetime(2024, 1, 1, tzinfo=timezone.utc)

        mock_db.refresh.side_effect = mock_refresh

        result = await create_education(data=data, current_user=mock_user, db=mock_db)

        added_edu = mock_db.add.call_args[0][0]
        assert added_edu.is_current == 1
        assert added_edu.end_year is None

    @pytest.mark.asyncio
    async def test_update_education(self, mock_db, mock_user, mock_education):
        """update_education should modify the specified education's fields."""
        mock_education.user_id = mock_user.id
        mock_db.query.return_value.filter.return_value.first.return_value = mock_education

        data = EducationUpdate(degree="PhD")

        result = await update_education(
            education_id=mock_education.id,
            data=data,
            current_user=mock_user,
            db=mock_db,
        )

        assert mock_education.degree == "PhD"
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_education_set_current_clears_end_year(
        self, mock_db, mock_user, mock_education
    ):
        """Setting is_current=True in update should clear end_year."""
        mock_education.user_id = mock_user.id
        mock_education.end_year = 2020
        mock_db.query.return_value.filter.return_value.first.return_value = mock_education

        data = EducationUpdate(is_current=True)

        result = await update_education(
            education_id=mock_education.id,
            data=data,
            current_user=mock_user,
            db=mock_db,
        )

        assert mock_education.is_current == 1
        assert mock_education.end_year is None

    @pytest.mark.asyncio
    async def test_delete_education(self, mock_db, mock_user, mock_education):
        """delete_education should remove the education from the database."""
        mock_education.user_id = mock_user.id
        mock_db.query.return_value.filter.return_value.first.return_value = mock_education

        await delete_education(
            education_id=mock_education.id,
            current_user=mock_user,
            db=mock_db,
        )

        mock_db.delete.assert_called_once_with(mock_education)
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_cannot_modify_other_users_education(self, mock_db, mock_user):
        """Updating another user's education should raise 404."""
        mock_db.query.return_value.filter.return_value.first.return_value = None

        data = EducationUpdate(institution="Hacked University")

        with pytest.raises(HTTPException) as exc_info:
            await update_education(
                education_id="other-edu-id",
                data=data,
                current_user=mock_user,
                db=mock_db,
            )
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Education not found"

    @pytest.mark.asyncio
    async def test_cannot_delete_other_users_education(self, mock_db, mock_user):
        """Deleting another user's education should raise 404."""
        mock_db.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            await delete_education(
                education_id="other-edu-id",
                current_user=mock_user,
                db=mock_db,
            )
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Education not found"
