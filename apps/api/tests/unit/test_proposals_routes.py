"""Tests for proposal route handlers (api/routes/proposals.py).

Covers proposal creation, listing, detail, update, and course completion.
Tests cover both company and talent perspectives, access control,
status transitions, and progress computation.
"""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch, AsyncMock
from uuid import uuid4

import pytest
from fastapi import HTTPException

from api.routes.proposals import (
    create_proposal,
    list_proposals,
    get_proposal,
    update_proposal,
    complete_proposal_course,
    get_current_company_user,
    _build_proposal_response,
)
from api.schemas.proposal import ProposalCreate, ProposalUpdate


# --- get_current_company_user dependency ---


class TestGetCurrentCompanyUser:
    """Tests for the get_current_company_user dependency."""

    @pytest.mark.asyncio
    async def test_allows_company_user(self, mock_company_user):
        """Should return the user if user_type is 'company'."""
        result = await get_current_company_user(current_user=mock_company_user)
        assert result.user_type == "company"

    @pytest.mark.asyncio
    async def test_rejects_talent_user(self, mock_user):
        """Should raise 403 if user_type is 'talent'."""
        with pytest.raises(HTTPException) as exc_info:
            await get_current_company_user(current_user=mock_user)
        assert exc_info.value.status_code == 403
        assert "Only company accounts" in exc_info.value.detail


# --- _build_proposal_response helper ---


class TestBuildProposalResponse:
    """Tests for the _build_proposal_response helper function."""

    def test_computes_progress_zero(self, mock_proposal, mock_company_user, mock_user, mock_proposal_course, mock_course):
        """Progress should be 0.0 when no courses are completed."""
        courses_map = {mock_course.id: mock_course}
        response = _build_proposal_response(
            mock_proposal, mock_company_user, mock_user,
            [mock_proposal_course], courses_map,
        )
        assert response.progress == 0.0
        assert response.company_name == "TechFlow Italia"
        assert response.talent_name == mock_user.full_name

    def test_computes_progress_full(self, mock_proposal, mock_company_user, mock_user, mock_proposal_course, mock_course):
        """Progress should be 1.0 when all courses are completed."""
        mock_proposal_course.is_completed = 1
        courses_map = {mock_course.id: mock_course}
        response = _build_proposal_response(
            mock_proposal, mock_company_user, mock_user,
            [mock_proposal_course], courses_map,
        )
        assert response.progress == 1.0

    def test_computes_progress_partial(self, mock_proposal, mock_company_user, mock_user, mock_course):
        """Progress should be 0.5 when half of courses are completed."""
        pc1 = MagicMock()
        pc1.id = str(uuid4())
        pc1.course_id = mock_course.id
        pc1.order = 0
        pc1.is_completed = 1
        pc1.completed_at = datetime(2024, 8, 1, tzinfo=timezone.utc)

        course2 = MagicMock()
        course2.id = str(uuid4())
        course2.title = "Advanced ML"
        course2.provider = "Udemy"
        course2.level = "advanced"

        pc2 = MagicMock()
        pc2.id = str(uuid4())
        pc2.course_id = course2.id
        pc2.order = 1
        pc2.is_completed = 0
        pc2.completed_at = None

        courses_map = {mock_course.id: mock_course, course2.id: course2}
        response = _build_proposal_response(
            mock_proposal, mock_company_user, mock_user,
            [pc1, pc2], courses_map,
        )
        assert response.progress == 0.5

    def test_empty_courses_progress_zero(self, mock_proposal, mock_company_user, mock_user):
        """Progress should be 0.0 when there are no courses."""
        response = _build_proposal_response(
            mock_proposal, mock_company_user, mock_user, [], {},
        )
        assert response.progress == 0.0
        assert response.courses == []

    def test_courses_sorted_by_order(self, mock_proposal, mock_company_user, mock_user, mock_course):
        """Courses in response should be sorted by order."""
        course2 = MagicMock()
        course2.id = str(uuid4())
        course2.title = "Course 2"
        course2.provider = "Udemy"
        course2.level = "beginner"

        pc1 = MagicMock()
        pc1.id = str(uuid4())
        pc1.course_id = course2.id
        pc1.order = 1
        pc1.is_completed = 0
        pc1.completed_at = None

        pc0 = MagicMock()
        pc0.id = str(uuid4())
        pc0.course_id = mock_course.id
        pc0.order = 0
        pc0.is_completed = 0
        pc0.completed_at = None

        courses_map = {mock_course.id: mock_course, course2.id: course2}
        response = _build_proposal_response(
            mock_proposal, mock_company_user, mock_user,
            [pc1, pc0], courses_map,
        )
        assert response.courses[0].order == 0
        assert response.courses[1].order == 1


# --- POST /proposals ---


class TestCreateProposal:
    """Tests for the POST /proposals endpoint."""

    @pytest.mark.asyncio
    async def test_create_proposal_success(self, mock_db, mock_company_user, mock_user, mock_course):
        """Company should be able to create a proposal with valid data."""
        mock_user.is_public = 1
        mock_user.is_active = 1

        # First filter call returns talent, second returns courses
        query_mock = MagicMock()
        filter_calls = []

        def side_effect_filter(*args, **kwargs):
            call_mock = MagicMock()
            filter_calls.append(call_mock)
            if len(filter_calls) == 1:
                # Talent lookup
                call_mock.first.return_value = mock_user
            elif len(filter_calls) == 2:
                # Course lookup
                call_mock.all.return_value = [mock_course]
            else:
                # After commit: company, talent, proposal_courses, courses
                call_mock.first.return_value = mock_company_user
                call_mock.all.return_value = []
            return call_mock

        mock_db.query.return_value.filter.side_effect = side_effect_filter

        def mock_refresh(obj):
            if not hasattr(obj, 'id') or obj.id is None:
                obj.id = str(uuid4())

        mock_db.refresh.side_effect = mock_refresh

        data = ProposalCreate(
            talent_id=mock_user.id,
            message="We want to work with you.",
            budget_range="5000-8000",
            course_ids=[mock_course.id],
        )

        result = await create_proposal(data=data, current_user=mock_company_user, db=mock_db)
        assert result.company_name == "TechFlow Italia"
        assert result.status == "sent"
        assert len(result.courses) == 1
        mock_db.add.assert_called()
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_proposal_talent_not_found(self, mock_db, mock_company_user, mock_course):
        """Should raise 404 when talent does not exist."""
        mock_db.query.return_value.filter.return_value.first.return_value = None

        data = ProposalCreate(
            talent_id=str(uuid4()),
            course_ids=[mock_course.id],
        )

        with pytest.raises(HTTPException) as exc_info:
            await create_proposal(data=data, current_user=mock_company_user, db=mock_db)
        assert exc_info.value.status_code == 404
        assert "Talent not found" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_create_proposal_course_not_found(self, mock_db, mock_company_user, mock_user):
        """Should raise 404 when one or more courses don't exist."""
        mock_user.is_public = 1
        mock_user.is_active = 1

        filter_calls = []

        def side_effect_filter(*args, **kwargs):
            call_mock = MagicMock()
            filter_calls.append(call_mock)
            if len(filter_calls) == 1:
                call_mock.first.return_value = mock_user
            else:
                call_mock.all.return_value = []  # No courses found
            return call_mock

        mock_db.query.return_value.filter.side_effect = side_effect_filter

        data = ProposalCreate(
            talent_id=mock_user.id,
            course_ids=[str(uuid4())],
        )

        with pytest.raises(HTTPException) as exc_info:
            await create_proposal(data=data, current_user=mock_company_user, db=mock_db)
        assert exc_info.value.status_code == 404
        assert "courses not found" in exc_info.value.detail

    def test_create_proposal_empty_courses_validation(self):
        """Should fail Pydantic validation with empty course_ids."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            ProposalCreate(
                talent_id=str(uuid4()),
                course_ids=[],
            )

    @pytest.mark.asyncio
    async def test_create_proposal_preserves_course_order(self, mock_db, mock_company_user, mock_user):
        """Courses should be created with correct order indices."""
        mock_user.is_public = 1
        mock_user.is_active = 1

        course1 = MagicMock()
        course1.id = str(uuid4())
        course1.title = "Course 1"
        course1.provider = "Coursera"
        course1.level = "beginner"
        course1.is_active = 1

        course2 = MagicMock()
        course2.id = str(uuid4())
        course2.title = "Course 2"
        course2.provider = "Udemy"
        course2.level = "intermediate"
        course2.is_active = 1

        filter_calls = []

        def side_effect_filter(*args, **kwargs):
            call_mock = MagicMock()
            filter_calls.append(call_mock)
            if len(filter_calls) == 1:
                call_mock.first.return_value = mock_user
            elif len(filter_calls) == 2:
                call_mock.all.return_value = [course1, course2]
            else:
                call_mock.first.return_value = mock_company_user
                call_mock.all.return_value = []
            return call_mock

        mock_db.query.return_value.filter.side_effect = side_effect_filter

        def mock_refresh(obj):
            if not hasattr(obj, 'id') or obj.id is None:
                obj.id = str(uuid4())

        mock_db.refresh.side_effect = mock_refresh

        data = ProposalCreate(
            talent_id=mock_user.id,
            course_ids=[course1.id, course2.id],
        )

        result = await create_proposal(data=data, current_user=mock_company_user, db=mock_db)
        assert result.courses[0].order == 0
        assert result.courses[1].order == 1


# --- GET /proposals ---


class TestListProposals:
    """Tests for the GET /proposals endpoint."""

    @pytest.mark.asyncio
    async def test_list_proposals_company_view(self, mock_db, mock_company_user):
        """Company should see their own proposals."""
        mock_query = MagicMock()
        mock_db.query.return_value.filter.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 0
        mock_query.order_by.return_value.offset.return_value.limit.return_value.all.return_value = []

        result = await list_proposals(
            page=1, page_size=10, proposal_status=None,
            current_user=mock_company_user, db=mock_db,
        )
        assert result.total == 0
        assert result.items == []
        assert result.page == 1

    @pytest.mark.asyncio
    async def test_list_proposals_talent_view(self, mock_db, mock_user):
        """Talent should see proposals, excluding drafts."""
        mock_query = MagicMock()
        mock_db.query.return_value.filter.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 0
        mock_query.order_by.return_value.offset.return_value.limit.return_value.all.return_value = []

        result = await list_proposals(
            page=1, page_size=10, proposal_status=None,
            current_user=mock_user, db=mock_db,
        )
        assert result.total == 0
        assert result.items == []

    @pytest.mark.asyncio
    async def test_list_proposals_with_status_filter(self, mock_db, mock_company_user):
        """Status filter should be applied to the query."""
        mock_query = MagicMock()
        mock_db.query.return_value.filter.return_value = mock_query
        # After status filter
        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 0
        mock_query.order_by.return_value.offset.return_value.limit.return_value.all.return_value = []

        result = await list_proposals(
            page=1, page_size=10, proposal_status="accepted",
            current_user=mock_company_user, db=mock_db,
        )
        assert result.total == 0

    @pytest.mark.asyncio
    async def test_list_proposals_pagination(self, mock_db, mock_company_user):
        """Pagination parameters should be applied correctly."""
        mock_query = MagicMock()
        mock_db.query.return_value.filter.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 25
        mock_query.order_by.return_value.offset.return_value.limit.return_value.all.return_value = []

        result = await list_proposals(
            page=3, page_size=5, proposal_status=None,
            current_user=mock_company_user, db=mock_db,
        )
        assert result.total == 25
        assert result.page == 3
        assert result.page_size == 5


# --- GET /proposals/{id} ---


class TestGetProposal:
    """Tests for the GET /proposals/{id} endpoint."""

    @pytest.mark.asyncio
    async def test_get_proposal_as_company_owner(self, mock_db, mock_company_user, mock_user, mock_proposal, mock_course, mock_proposal_course):
        """Company owner should see proposal detail."""
        filter_calls = []

        def side_effect_filter(*args, **kwargs):
            call_mock = MagicMock()
            filter_calls.append(call_mock)
            if len(filter_calls) == 1:
                call_mock.first.return_value = mock_proposal
            elif len(filter_calls) == 2:
                call_mock.first.return_value = mock_company_user
            elif len(filter_calls) == 3:
                call_mock.first.return_value = mock_user
            elif len(filter_calls) == 4:
                call_mock.all.return_value = [mock_proposal_course]
            else:
                call_mock.all.return_value = [mock_course]
            return call_mock

        mock_db.query.return_value.filter.side_effect = side_effect_filter

        result = await get_proposal(
            proposal_id=mock_proposal.id,
            current_user=mock_company_user, db=mock_db,
        )
        assert result.id == mock_proposal.id
        assert result.status == "sent"

    @pytest.mark.asyncio
    async def test_get_proposal_not_found(self, mock_db, mock_company_user):
        """Should raise 404 when proposal does not exist."""
        mock_db.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            await get_proposal(
                proposal_id=str(uuid4()),
                current_user=mock_company_user, db=mock_db,
            )
        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_get_proposal_non_owner_returns_404(self, mock_db, mock_proposal):
        """Non-owner should receive 404 (not 403, to prevent enumeration)."""
        mock_db.query.return_value.filter.return_value.first.return_value = mock_proposal

        other_user = MagicMock()
        other_user.id = str(uuid4())
        other_user.user_type = "talent"

        with pytest.raises(HTTPException) as exc_info:
            await get_proposal(
                proposal_id=mock_proposal.id,
                current_user=other_user, db=mock_db,
            )
        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_get_proposal_talent_cant_see_draft(self, mock_db, mock_user, mock_proposal):
        """Talent should not see draft proposals."""
        mock_proposal.status = "draft"
        mock_db.query.return_value.filter.return_value.first.return_value = mock_proposal

        with pytest.raises(HTTPException) as exc_info:
            await get_proposal(
                proposal_id=mock_proposal.id,
                current_user=mock_user, db=mock_db,
            )
        assert exc_info.value.status_code == 404


# --- PATCH /proposals/{id} ---


class TestUpdateProposal:
    """Tests for the PATCH /proposals/{id} endpoint."""

    @pytest.mark.asyncio
    async def test_talent_accepts_proposal(self, mock_db, mock_user, mock_proposal, mock_company_user, mock_course, mock_proposal_course):
        """Talent should be able to accept a sent proposal."""
        mock_proposal.status = "sent"

        filter_calls = []

        def side_effect_filter(*args, **kwargs):
            call_mock = MagicMock()
            filter_calls.append(call_mock)
            if len(filter_calls) == 1:
                call_mock.first.return_value = mock_proposal
            elif len(filter_calls) == 2:
                call_mock.first.return_value = mock_company_user
            elif len(filter_calls) == 3:
                call_mock.first.return_value = mock_user
            elif len(filter_calls) == 4:
                call_mock.all.return_value = [mock_proposal_course]
            else:
                call_mock.all.return_value = [mock_course]
            return call_mock

        mock_db.query.return_value.filter.side_effect = side_effect_filter

        data = ProposalUpdate(status="accepted")
        result = await update_proposal(
            proposal_id=mock_proposal.id, data=data,
            current_user=mock_user, db=mock_db,
        )
        assert mock_proposal.status == "accepted"
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_talent_rejects_proposal(self, mock_db, mock_user, mock_proposal, mock_company_user, mock_course, mock_proposal_course):
        """Talent should be able to reject a sent proposal."""
        mock_proposal.status = "sent"

        filter_calls = []

        def side_effect_filter(*args, **kwargs):
            call_mock = MagicMock()
            filter_calls.append(call_mock)
            if len(filter_calls) == 1:
                call_mock.first.return_value = mock_proposal
            elif len(filter_calls) == 2:
                call_mock.first.return_value = mock_company_user
            elif len(filter_calls) == 3:
                call_mock.first.return_value = mock_user
            elif len(filter_calls) == 4:
                call_mock.all.return_value = [mock_proposal_course]
            else:
                call_mock.all.return_value = [mock_course]
            return call_mock

        mock_db.query.return_value.filter.side_effect = side_effect_filter

        data = ProposalUpdate(status="rejected")
        result = await update_proposal(
            proposal_id=mock_proposal.id, data=data,
            current_user=mock_user, db=mock_db,
        )
        assert mock_proposal.status == "rejected"

    @pytest.mark.asyncio
    async def test_company_updates_draft_message(self, mock_db, mock_company_user, mock_proposal, mock_user, mock_course, mock_proposal_course):
        """Company should be able to update message on draft proposals."""
        mock_proposal.status = "draft"

        filter_calls = []

        def side_effect_filter(*args, **kwargs):
            call_mock = MagicMock()
            filter_calls.append(call_mock)
            if len(filter_calls) == 1:
                call_mock.first.return_value = mock_proposal
            elif len(filter_calls) == 2:
                call_mock.first.return_value = mock_company_user
            elif len(filter_calls) == 3:
                call_mock.first.return_value = mock_user
            elif len(filter_calls) == 4:
                call_mock.all.return_value = [mock_proposal_course]
            else:
                call_mock.all.return_value = [mock_course]
            return call_mock

        mock_db.query.return_value.filter.side_effect = side_effect_filter

        data = ProposalUpdate(message="Updated message")
        result = await update_proposal(
            proposal_id=mock_proposal.id, data=data,
            current_user=mock_company_user, db=mock_db,
        )
        assert mock_proposal.message == "Updated message"

    @pytest.mark.asyncio
    async def test_company_sends_draft(self, mock_db, mock_company_user, mock_proposal, mock_user, mock_course, mock_proposal_course):
        """Company should be able to send a draft proposal."""
        mock_proposal.status = "draft"

        filter_calls = []

        def side_effect_filter(*args, **kwargs):
            call_mock = MagicMock()
            filter_calls.append(call_mock)
            if len(filter_calls) == 1:
                call_mock.first.return_value = mock_proposal
            elif len(filter_calls) == 2:
                call_mock.first.return_value = mock_company_user
            elif len(filter_calls) == 3:
                call_mock.first.return_value = mock_user
            elif len(filter_calls) == 4:
                call_mock.all.return_value = [mock_proposal_course]
            else:
                call_mock.all.return_value = [mock_course]
            return call_mock

        mock_db.query.return_value.filter.side_effect = side_effect_filter

        data = ProposalUpdate(status="sent")
        result = await update_proposal(
            proposal_id=mock_proposal.id, data=data,
            current_user=mock_company_user, db=mock_db,
        )
        assert mock_proposal.status == "sent"

    @pytest.mark.asyncio
    async def test_company_invalid_transition(self, mock_db, mock_company_user, mock_proposal):
        """Company should not be able to make invalid status transitions."""
        mock_proposal.status = "sent"
        mock_db.query.return_value.filter.return_value.first.return_value = mock_proposal

        data = ProposalUpdate(status="completed")

        with pytest.raises(HTTPException) as exc_info:
            await update_proposal(
                proposal_id=mock_proposal.id, data=data,
                current_user=mock_company_user, db=mock_db,
            )
        assert exc_info.value.status_code == 400
        assert "Invalid status transition" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_talent_invalid_transition(self, mock_db, mock_user, mock_proposal):
        """Talent should not be able to accept a draft proposal."""
        mock_proposal.status = "draft"
        mock_db.query.return_value.filter.return_value.first.return_value = mock_proposal

        data = ProposalUpdate(status="accepted")

        with pytest.raises(HTTPException) as exc_info:
            await update_proposal(
                proposal_id=mock_proposal.id, data=data,
                current_user=mock_user, db=mock_db,
            )
        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_update_proposal_not_found(self, mock_db, mock_company_user):
        """Should raise 404 when proposal does not exist."""
        mock_db.query.return_value.filter.return_value.first.return_value = None

        data = ProposalUpdate(status="sent")

        with pytest.raises(HTTPException) as exc_info:
            await update_proposal(
                proposal_id=str(uuid4()), data=data,
                current_user=mock_company_user, db=mock_db,
            )
        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_non_owner_company_update(self, mock_db, mock_proposal):
        """Company that doesn't own the proposal should get 403."""
        mock_db.query.return_value.filter.return_value.first.return_value = mock_proposal

        other_company = MagicMock()
        other_company.id = str(uuid4())
        other_company.user_type = "company"

        data = ProposalUpdate(status="sent")

        with pytest.raises(HTTPException) as exc_info:
            await update_proposal(
                proposal_id=mock_proposal.id, data=data,
                current_user=other_company, db=mock_db,
            )
        assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_non_recipient_talent_update(self, mock_db, mock_proposal):
        """Talent that isn't the recipient should get 403."""
        mock_db.query.return_value.filter.return_value.first.return_value = mock_proposal

        other_talent = MagicMock()
        other_talent.id = str(uuid4())
        other_talent.user_type = "talent"

        data = ProposalUpdate(status="accepted")

        with pytest.raises(HTTPException) as exc_info:
            await update_proposal(
                proposal_id=mock_proposal.id, data=data,
                current_user=other_talent, db=mock_db,
            )
        assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_talent_cannot_update_message(self, mock_db, mock_user, mock_proposal):
        """Talent should not be able to update message without a status change."""
        mock_proposal.status = "sent"
        mock_db.query.return_value.filter.return_value.first.return_value = mock_proposal

        data = ProposalUpdate(message="Updated by talent")

        with pytest.raises(HTTPException) as exc_info:
            await update_proposal(
                proposal_id=mock_proposal.id, data=data,
                current_user=mock_user, db=mock_db,
            )
        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_company_cannot_update_message_on_sent(self, mock_db, mock_company_user, mock_proposal):
        """Company should not be able to update message on non-draft proposals."""
        mock_proposal.status = "sent"
        mock_db.query.return_value.filter.return_value.first.return_value = mock_proposal

        data = ProposalUpdate(message="Updated message")

        with pytest.raises(HTTPException) as exc_info:
            await update_proposal(
                proposal_id=mock_proposal.id, data=data,
                current_user=mock_company_user, db=mock_db,
            )
        assert exc_info.value.status_code == 400


# --- PATCH /proposals/{id}/courses/{course_id} ---


class TestCompleteProposalCourse:
    """Tests for the PATCH /proposals/{id}/courses/{course_id} endpoint."""

    @pytest.mark.asyncio
    async def test_talent_completes_course(self, mock_db, mock_user, mock_proposal, mock_proposal_course, mock_company_user, mock_course):
        """Talent should be able to mark a course as completed in an accepted proposal."""
        mock_proposal.status = "accepted"

        filter_calls = []

        def side_effect_filter(*args, **kwargs):
            call_mock = MagicMock()
            filter_calls.append(call_mock)
            if len(filter_calls) == 1:
                call_mock.first.return_value = mock_proposal
            elif len(filter_calls) == 2:
                call_mock.first.return_value = mock_proposal_course
            elif len(filter_calls) == 3:
                # all_proposal_courses - only this one, already completed
                call_mock.all.return_value = [mock_proposal_course]
            elif len(filter_calls) == 4:
                call_mock.first.return_value = mock_company_user
            elif len(filter_calls) == 5:
                call_mock.first.return_value = mock_user
            elif len(filter_calls) == 6:
                call_mock.all.return_value = [mock_proposal_course]
            else:
                call_mock.all.return_value = [mock_course]
            return call_mock

        mock_db.query.return_value.filter.side_effect = side_effect_filter

        result = await complete_proposal_course(
            proposal_id=mock_proposal.id,
            course_id=mock_course.id,
            current_user=mock_user, db=mock_db,
        )
        assert mock_proposal_course.is_completed == 1
        assert mock_proposal_course.completed_at is not None

    @pytest.mark.asyncio
    async def test_auto_complete_proposal_when_all_courses_done(self, mock_db, mock_user, mock_proposal, mock_company_user, mock_course):
        """Proposal should auto-complete when all courses are marked as completed."""
        mock_proposal.status = "accepted"

        # Single course already completed in the check
        pc = MagicMock()
        pc.id = str(uuid4())
        pc.proposal_id = mock_proposal.id
        pc.course_id = mock_course.id
        pc.order = 0
        pc.is_completed = 0  # Will be set to 1
        pc.completed_at = None

        filter_calls = []

        def side_effect_filter(*args, **kwargs):
            call_mock = MagicMock()
            filter_calls.append(call_mock)
            if len(filter_calls) == 1:
                call_mock.first.return_value = mock_proposal
            elif len(filter_calls) == 2:
                call_mock.first.return_value = pc
            elif len(filter_calls) == 3:
                call_mock.all.return_value = [pc]
            elif len(filter_calls) == 4:
                call_mock.first.return_value = mock_company_user
            elif len(filter_calls) == 5:
                call_mock.first.return_value = mock_user
            elif len(filter_calls) == 6:
                call_mock.all.return_value = [pc]
            else:
                call_mock.all.return_value = [mock_course]
            return call_mock

        mock_db.query.return_value.filter.side_effect = side_effect_filter

        result = await complete_proposal_course(
            proposal_id=mock_proposal.id,
            course_id=mock_course.id,
            current_user=mock_user, db=mock_db,
        )
        # The course completion happens in the route, and auto-complete sets status
        assert mock_proposal.status == "completed"

    @pytest.mark.asyncio
    async def test_company_cannot_complete_course(self, mock_db, mock_company_user):
        """Company should not be able to mark courses as completed."""
        with pytest.raises(HTTPException) as exc_info:
            await complete_proposal_course(
                proposal_id=str(uuid4()),
                course_id=str(uuid4()),
                current_user=mock_company_user, db=mock_db,
            )
        assert exc_info.value.status_code == 403
        assert "Only talents" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_complete_course_wrong_status(self, mock_db, mock_user, mock_proposal):
        """Should raise 400 when proposal is not in accepted status."""
        mock_proposal.status = "sent"

        mock_db.query.return_value.filter.return_value.first.return_value = mock_proposal

        with pytest.raises(HTTPException) as exc_info:
            await complete_proposal_course(
                proposal_id=mock_proposal.id,
                course_id=str(uuid4()),
                current_user=mock_user, db=mock_db,
            )
        assert exc_info.value.status_code == 400
        assert "must be accepted" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_complete_course_not_found(self, mock_db, mock_user, mock_proposal):
        """Should raise 404 when course is not in the proposal."""
        mock_proposal.status = "accepted"

        filter_calls = []

        def side_effect_filter(*args, **kwargs):
            call_mock = MagicMock()
            filter_calls.append(call_mock)
            if len(filter_calls) == 1:
                call_mock.first.return_value = mock_proposal
            else:
                call_mock.first.return_value = None
            return call_mock

        mock_db.query.return_value.filter.side_effect = side_effect_filter

        with pytest.raises(HTTPException) as exc_info:
            await complete_proposal_course(
                proposal_id=mock_proposal.id,
                course_id=str(uuid4()),
                current_user=mock_user, db=mock_db,
            )
        assert exc_info.value.status_code == 404
        assert "Course not found" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_complete_course_not_recipient(self, mock_db, mock_proposal):
        """Talent that isn't the recipient should get 403."""
        mock_proposal.status = "accepted"
        mock_db.query.return_value.filter.return_value.first.return_value = mock_proposal

        other_talent = MagicMock()
        other_talent.id = str(uuid4())
        other_talent.user_type = "talent"

        with pytest.raises(HTTPException) as exc_info:
            await complete_proposal_course(
                proposal_id=mock_proposal.id,
                course_id=str(uuid4()),
                current_user=other_talent, db=mock_db,
            )
        assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_complete_course_on_rejected_proposal(self, mock_db, mock_user, mock_proposal):
        """Should raise 400 when trying to complete a course on a rejected proposal."""
        mock_proposal.status = "rejected"

        mock_db.query.return_value.filter.return_value.first.return_value = mock_proposal

        with pytest.raises(HTTPException) as exc_info:
            await complete_proposal_course(
                proposal_id=mock_proposal.id,
                course_id=str(uuid4()),
                current_user=mock_user, db=mock_db,
            )
        assert exc_info.value.status_code == 400
        assert "must be accepted" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_complete_course_on_completed_proposal(self, mock_db, mock_user, mock_proposal):
        """Should raise 400 when trying to complete a course on an already completed proposal."""
        mock_proposal.status = "completed"

        mock_db.query.return_value.filter.return_value.first.return_value = mock_proposal

        with pytest.raises(HTTPException) as exc_info:
            await complete_proposal_course(
                proposal_id=mock_proposal.id,
                course_id=str(uuid4()),
                current_user=mock_user, db=mock_db,
            )
        assert exc_info.value.status_code == 400
        assert "must be accepted" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_complete_already_completed_course(self, mock_db, mock_user, mock_proposal, mock_proposal_course):
        """Should raise 400 when trying to complete an already completed course."""
        mock_proposal.status = "accepted"
        mock_proposal_course.is_completed = 1
        mock_proposal_course.completed_at = datetime(2024, 8, 1, tzinfo=timezone.utc)

        filter_calls = []

        def side_effect_filter(*args, **kwargs):
            call_mock = MagicMock()
            filter_calls.append(call_mock)
            if len(filter_calls) == 1:
                call_mock.first.return_value = mock_proposal
            else:
                call_mock.first.return_value = mock_proposal_course
            return call_mock

        mock_db.query.return_value.filter.side_effect = side_effect_filter

        with pytest.raises(HTTPException) as exc_info:
            await complete_proposal_course(
                proposal_id=mock_proposal.id,
                course_id=mock_proposal_course.course_id,
                current_user=mock_user, db=mock_db,
            )
        assert exc_info.value.status_code == 400
        assert "already completed" in exc_info.value.detail


# --- Edge cases and security tests ---


class TestProposalEdgeCases:
    """Tests for edge cases and security validations in proposals."""

    @pytest.mark.asyncio
    async def test_create_proposal_self_proposal_rejected(self, mock_db, mock_company_user):
        """Company should not be able to create a proposal targeting themselves."""
        data = ProposalCreate(
            talent_id=mock_company_user.id,
            course_ids=[str(uuid4())],
        )

        with pytest.raises(HTTPException) as exc_info:
            await create_proposal(data=data, current_user=mock_company_user, db=mock_db)
        assert exc_info.value.status_code == 400
        assert "Cannot create a proposal for yourself" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_create_proposal_duplicate_course_ids_rejected(self, mock_db, mock_company_user):
        """Duplicate course_ids should be rejected with 400."""
        course_id = str(uuid4())
        data = ProposalCreate(
            talent_id=str(uuid4()),
            course_ids=[course_id, course_id],
        )

        with pytest.raises(HTTPException) as exc_info:
            await create_proposal(data=data, current_user=mock_company_user, db=mock_db)
        assert exc_info.value.status_code == 400
        assert "Duplicate course_ids" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_create_proposal_target_must_be_talent_user_type(self, mock_db, mock_company_user):
        """Proposal target must be a talent, not another company user."""
        target_company = MagicMock()
        target_company.id = str(uuid4())
        target_company.user_type = "company"
        target_company.is_public = 1
        target_company.is_active = 1

        # The filter includes User.user_type == "talent", so a company user won't be found
        mock_db.query.return_value.filter.return_value.first.return_value = None

        data = ProposalCreate(
            talent_id=target_company.id,
            course_ids=[str(uuid4())],
        )

        with pytest.raises(HTTPException) as exc_info:
            await create_proposal(data=data, current_user=mock_company_user, db=mock_db)
        assert exc_info.value.status_code == 404
        assert "Talent not found" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_update_proposal_empty_body_rejected(self, mock_db, mock_company_user, mock_proposal):
        """Empty update body should be rejected with 400."""
        mock_db.query.return_value.filter.return_value.first.return_value = mock_proposal

        data = ProposalUpdate()  # no fields set

        with pytest.raises(HTTPException) as exc_info:
            await update_proposal(
                proposal_id=mock_proposal.id, data=data,
                current_user=mock_company_user, db=mock_db,
            )
        assert exc_info.value.status_code == 400
        assert "No fields to update" in exc_info.value.detail

    def test_build_proposal_response_null_safe_company(self, mock_proposal, mock_user, mock_proposal_course, mock_course):
        """_build_proposal_response should handle None company gracefully."""
        courses_map = {mock_course.id: mock_course}
        response = _build_proposal_response(
            mock_proposal, None, mock_user,
            [mock_proposal_course], courses_map,
        )
        assert response.company_name == "Unknown"

    def test_build_proposal_response_null_safe_talent(self, mock_proposal, mock_company_user, mock_proposal_course, mock_course):
        """_build_proposal_response should handle None talent gracefully."""
        courses_map = {mock_course.id: mock_course}
        response = _build_proposal_response(
            mock_proposal, mock_company_user, None,
            [mock_proposal_course], courses_map,
        )
        assert response.talent_name == "Unknown"

    @pytest.mark.asyncio
    async def test_company_cannot_update_message_on_sent_with_status_transition(self, mock_db, mock_company_user, mock_proposal):
        """Company should not be able to sneak message updates into a status transition on non-draft proposals."""
        mock_proposal.status = "sent"
        mock_db.query.return_value.filter.return_value.first.return_value = mock_proposal

        # Try to send both status and message on a sent proposal
        data = ProposalUpdate(status="sent", message="sneaky update")

        with pytest.raises(HTTPException) as exc_info:
            await update_proposal(
                proposal_id=mock_proposal.id, data=data,
                current_user=mock_company_user, db=mock_db,
            )
        # Should fail because sent->sent is an invalid transition
        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_talent_cannot_accept_already_accepted_proposal(self, mock_db, mock_user, mock_proposal):
        """Talent should not be able to re-accept an already accepted proposal."""
        mock_proposal.status = "accepted"
        mock_db.query.return_value.filter.return_value.first.return_value = mock_proposal

        data = ProposalUpdate(status="accepted")

        with pytest.raises(HTTPException) as exc_info:
            await update_proposal(
                proposal_id=mock_proposal.id, data=data,
                current_user=mock_user, db=mock_db,
            )
        assert exc_info.value.status_code == 400
        assert "Invalid status transition" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_talent_cannot_reject_already_rejected_proposal(self, mock_db, mock_user, mock_proposal):
        """Talent should not be able to re-reject an already rejected proposal."""
        mock_proposal.status = "rejected"
        mock_db.query.return_value.filter.return_value.first.return_value = mock_proposal

        data = ProposalUpdate(status="rejected")

        with pytest.raises(HTTPException) as exc_info:
            await update_proposal(
                proposal_id=mock_proposal.id, data=data,
                current_user=mock_user, db=mock_db,
            )
        assert exc_info.value.status_code == 400
        assert "Invalid status transition" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_talent_cannot_reject_completed_proposal(self, mock_db, mock_user, mock_proposal):
        """Talent should not be able to reject a completed proposal."""
        mock_proposal.status = "completed"
        mock_db.query.return_value.filter.return_value.first.return_value = mock_proposal

        data = ProposalUpdate(status="rejected")

        with pytest.raises(HTTPException) as exc_info:
            await update_proposal(
                proposal_id=mock_proposal.id, data=data,
                current_user=mock_user, db=mock_db,
            )
        assert exc_info.value.status_code == 400
        assert "Invalid status transition" in exc_info.value.detail
