"""Tests for proposal route handlers (api/routes/proposals/).

Covers proposal creation, listing, detail, update, course completion,
course start, notes, company-update, dashboard, hiring, and gamification.
Tests cover both company and talent perspectives, access control,
status transitions, progress computation, XP, milestones, and messages.
"""

from __future__ import annotations

from datetime import datetime, timezone, timedelta
from unittest.mock import MagicMock, patch, AsyncMock
from uuid import uuid4

import pytest
from fastapi import HTTPException

from api.routes.proposals.router import (
    create_proposal,
    list_proposals,
    get_proposal,
    get_proposal_dashboard,
    update_proposal,
    complete_proposal_course,
    start_proposal_course,
    update_course_notes,
    update_course_company,
    get_current_company_user,
    _build_proposal_response,
    _xp_for_level,
)
from api.routes.proposals.schemas import (
    ProposalCreate,
    ProposalUpdate,
    CourseNotesUpdate,
    CompanyCourseUpdate,
)


def _make_proposal_course(proposal_id, course_id, order=0, is_completed=0, completed_at=None, started_at=None, talent_notes=None, company_notes=None, deadline=None, xp_earned=0):
    """Helper to create a fully-formed mock ProposalCourse."""
    pc = MagicMock()
    pc.id = str(uuid4())
    pc.proposal_id = proposal_id
    pc.course_id = course_id
    pc.order = order
    pc.is_completed = is_completed
    pc.completed_at = completed_at
    pc.started_at = started_at
    pc.talent_notes = talent_notes
    pc.company_notes = company_notes
    pc.deadline = deadline
    pc.xp_earned = xp_earned
    pc.created_at = datetime(2024, 7, 1, tzinfo=timezone.utc)
    return pc


def _make_course(course_id=None, title="Test Course", provider="Coursera", level="intermediate", url="https://example.com", duration="8 weeks", category="ML"):
    """Helper to create a fully-formed mock Course."""
    course = MagicMock()
    course.id = course_id or str(uuid4())
    course.title = title
    course.provider = provider
    course.level = level
    course.url = url
    course.duration = duration
    course.category = category
    course.is_active = 1
    return course


def _make_milestone(proposal_id, milestone_type="course_completed", title="Corso completato", xp_reward=200):
    """Helper to create a fully-formed mock ProposalMilestone."""
    m = MagicMock()
    m.id = str(uuid4())
    m.proposal_id = proposal_id
    m.milestone_type = milestone_type
    m.title = title
    m.description = None
    m.xp_reward = xp_reward
    m.achieved_at = datetime(2024, 8, 1, tzinfo=timezone.utc)
    return m


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
        pc1 = _make_proposal_course(mock_proposal.id, mock_course.id, order=0, is_completed=1, completed_at=datetime(2024, 8, 1, tzinfo=timezone.utc))

        course2 = _make_course(title="Advanced ML", provider="Udemy", level="advanced")

        pc2 = _make_proposal_course(mock_proposal.id, course2.id, order=1)

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
        course2 = _make_course(title="Course 2", provider="Udemy", level="beginner")

        pc1 = _make_proposal_course(mock_proposal.id, course2.id, order=1)
        pc0 = _make_proposal_course(mock_proposal.id, mock_course.id, order=0)

        courses_map = {mock_course.id: mock_course, course2.id: course2}
        response = _build_proposal_response(
            mock_proposal, mock_company_user, mock_user,
            [pc1, pc0], courses_map,
        )
        assert response.courses[0].order == 0
        assert response.courses[1].order == 1

    def test_includes_milestones(self, mock_proposal, mock_company_user, mock_user, mock_proposal_course, mock_course):
        """Response should include milestones when provided."""
        milestone = _make_milestone(mock_proposal.id)
        courses_map = {mock_course.id: mock_course}
        response = _build_proposal_response(
            mock_proposal, mock_company_user, mock_user,
            [mock_proposal_course], courses_map,
            milestones=[milestone],
        )
        assert len(response.milestones) == 1
        assert response.milestones[0].milestone_type == "course_completed"

    def test_includes_total_xp(self, mock_proposal, mock_company_user, mock_user):
        """Response should include total_xp."""
        mock_proposal.total_xp = 350
        response = _build_proposal_response(
            mock_proposal, mock_company_user, mock_user, [], {},
        )
        assert response.total_xp == 350

    def test_includes_hired_fields(self, mock_proposal, mock_company_user, mock_user):
        """Response should include hired_at and hiring_notes when set."""
        hired_time = datetime(2024, 9, 1, tzinfo=timezone.utc)
        mock_proposal.hired_at = hired_time
        mock_proposal.hiring_notes = "Great candidate"
        response = _build_proposal_response(
            mock_proposal, mock_company_user, mock_user, [], {},
        )
        assert response.hired_at == hired_time
        assert response.hiring_notes == "Great candidate"

    def test_includes_course_enriched_fields(self, mock_proposal, mock_company_user, mock_user, mock_course):
        """Response courses should include url, duration, category from Course model."""
        pc = _make_proposal_course(mock_proposal.id, mock_course.id)
        courses_map = {mock_course.id: mock_course}
        response = _build_proposal_response(
            mock_proposal, mock_company_user, mock_user,
            [pc], courses_map,
        )
        assert response.courses[0].course_url == mock_course.url
        assert response.courses[0].course_duration == mock_course.duration
        assert response.courses[0].course_category == mock_course.category

    def test_computes_is_overdue(self, mock_proposal, mock_company_user, mock_user, mock_course):
        """is_overdue should be True when deadline has passed and course not completed."""
        pc = _make_proposal_course(
            mock_proposal.id, mock_course.id,
            deadline=datetime(2024, 1, 1, tzinfo=timezone.utc),
        )
        courses_map = {mock_course.id: mock_course}
        response = _build_proposal_response(
            mock_proposal, mock_company_user, mock_user,
            [pc], courses_map,
        )
        assert response.courses[0].is_overdue is True
        assert response.courses[0].days_remaining is not None
        assert response.courses[0].days_remaining < 0

    def test_computes_days_remaining(self, mock_proposal, mock_company_user, mock_user, mock_course):
        """days_remaining should be computed from deadline."""
        future = datetime.now(timezone.utc) + timedelta(days=10)
        pc = _make_proposal_course(
            mock_proposal.id, mock_course.id,
            deadline=future,
        )
        courses_map = {mock_course.id: mock_course}
        response = _build_proposal_response(
            mock_proposal, mock_company_user, mock_user,
            [pc], courses_map,
        )
        assert response.courses[0].is_overdue is False
        assert response.courses[0].days_remaining >= 9


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
                # After commit: company, talent, proposal_courses, courses, milestones
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
        mock_db.commit.assert_called()  # May be called multiple times due to email notifications

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

        course1 = _make_course(title="Course 1", provider="Coursera", level="beginner")
        course2 = _make_course(title="Course 2", provider="Udemy", level="intermediate")

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

    def _setup_get_proposal_mocks(self, mock_db, mock_proposal, mock_company_user, mock_user, mock_proposal_course, mock_course):
        """Setup filter side_effect for get_proposal tests."""
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
            elif len(filter_calls) == 5:
                call_mock.all.return_value = [mock_course]
            else:
                # milestones
                call_mock.all.return_value = []
            return call_mock

        mock_db.query.return_value.filter.side_effect = side_effect_filter

    @pytest.mark.asyncio
    async def test_get_proposal_as_company_owner(self, mock_db, mock_company_user, mock_user, mock_proposal, mock_course, mock_proposal_course):
        """Company owner should see proposal detail."""
        self._setup_get_proposal_mocks(mock_db, mock_proposal, mock_company_user, mock_user, mock_proposal_course, mock_course)

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


# --- GET /proposals/{id}/dashboard ---


class TestGetProposalDashboard:
    """Tests for the GET /proposals/{id}/dashboard endpoint."""

    @pytest.mark.asyncio
    async def test_dashboard_returns_enriched_response(self, mock_db, mock_company_user, mock_user, mock_proposal, mock_course, mock_proposal_course):
        """Dashboard should return enriched ProposalResponse."""
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
            elif len(filter_calls) == 5:
                call_mock.all.return_value = [mock_course]
            else:
                call_mock.all.return_value = []
            return call_mock

        mock_db.query.return_value.filter.side_effect = side_effect_filter

        result = await get_proposal_dashboard(
            proposal_id=mock_proposal.id,
            current_user=mock_company_user, db=mock_db,
        )
        assert result.id == mock_proposal.id

    @pytest.mark.asyncio
    async def test_dashboard_not_found(self, mock_db, mock_company_user):
        """Should raise 404 when proposal does not exist."""
        mock_db.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            await get_proposal_dashboard(
                proposal_id=str(uuid4()),
                current_user=mock_company_user, db=mock_db,
            )
        assert exc_info.value.status_code == 404


# --- PATCH /proposals/{id} ---


class TestUpdateProposal:
    """Tests for the PATCH /proposals/{id} endpoint."""

    def _setup_update_success_mocks(self, mock_db, mock_proposal, mock_company_user, mock_user, mock_proposal_course, mock_course):
        """Setup filter side_effect for successful update tests."""
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
            elif len(filter_calls) == 5:
                call_mock.all.return_value = [mock_course]
            else:
                call_mock.all.return_value = []
            return call_mock

        mock_db.query.return_value.filter.side_effect = side_effect_filter

    @pytest.mark.asyncio
    async def test_talent_accepts_proposal(self, mock_db, mock_user, mock_proposal, mock_company_user, mock_course, mock_proposal_course):
        """Talent should be able to accept a sent proposal."""
        mock_proposal.status = "sent"
        self._setup_update_success_mocks(mock_db, mock_proposal, mock_company_user, mock_user, mock_proposal_course, mock_course)

        data = ProposalUpdate(status="accepted")
        result = await update_proposal(
            proposal_id=mock_proposal.id, data=data,
            current_user=mock_user, db=mock_db,
        )
        assert mock_proposal.status == "accepted"
        mock_db.commit.assert_called()  # May be called multiple times due to email notifications

    @pytest.mark.asyncio
    async def test_talent_rejects_proposal(self, mock_db, mock_user, mock_proposal, mock_company_user, mock_course, mock_proposal_course):
        """Talent should be able to reject a sent proposal."""
        mock_proposal.status = "sent"
        self._setup_update_success_mocks(mock_db, mock_proposal, mock_company_user, mock_user, mock_proposal_course, mock_course)

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
        self._setup_update_success_mocks(mock_db, mock_proposal, mock_company_user, mock_user, mock_proposal_course, mock_course)

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
        self._setup_update_success_mocks(mock_db, mock_proposal, mock_company_user, mock_user, mock_proposal_course, mock_course)

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
                # Course lookup for XP
                call_mock.first.return_value = mock_course
            elif len(filter_calls) == 4:
                # all_proposal_courses
                call_mock.all.return_value = [mock_proposal_course]
            elif len(filter_calls) == 5:
                # existing milestones
                call_mock.all.return_value = []
            elif len(filter_calls) == 6:
                call_mock.first.return_value = mock_company_user
            elif len(filter_calls) == 7:
                call_mock.first.return_value = mock_user
            elif len(filter_calls) == 8:
                call_mock.all.return_value = [mock_proposal_course]
            elif len(filter_calls) == 9:
                call_mock.all.return_value = [mock_course]
            else:
                call_mock.all.return_value = []
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

        pc = _make_proposal_course(mock_proposal.id, mock_course.id)

        filter_calls = []

        def side_effect_filter(*args, **kwargs):
            call_mock = MagicMock()
            filter_calls.append(call_mock)
            if len(filter_calls) == 1:
                call_mock.first.return_value = mock_proposal
            elif len(filter_calls) == 2:
                call_mock.first.return_value = pc
            elif len(filter_calls) == 3:
                # Course lookup for XP
                call_mock.first.return_value = mock_course
            elif len(filter_calls) == 4:
                # all_proposal_courses
                call_mock.all.return_value = [pc]
            elif len(filter_calls) == 5:
                # existing milestones
                call_mock.all.return_value = []
            elif len(filter_calls) == 6:
                call_mock.first.return_value = mock_company_user
            elif len(filter_calls) == 7:
                call_mock.first.return_value = mock_user
            elif len(filter_calls) == 8:
                call_mock.all.return_value = [pc]
            elif len(filter_calls) == 9:
                call_mock.all.return_value = [mock_course]
            else:
                call_mock.all.return_value = []
            return call_mock

        mock_db.query.return_value.filter.side_effect = side_effect_filter

        result = await complete_proposal_course(
            proposal_id=mock_proposal.id,
            course_id=mock_course.id,
            current_user=mock_user, db=mock_db,
        )
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


# --- Gamification: XP calculation ---


class TestXPCalculation:
    """Tests for XP calculation based on course level."""

    def test_xp_beginner(self):
        """Beginner courses should earn 100 XP."""
        assert _xp_for_level("beginner") == 100

    def test_xp_intermediate(self):
        """Intermediate courses should earn 200 XP."""
        assert _xp_for_level("intermediate") == 200

    def test_xp_advanced(self):
        """Advanced courses should earn 300 XP."""
        assert _xp_for_level("advanced") == 300

    def test_xp_unknown_defaults_to_100(self):
        """Unknown level should default to 100 XP."""
        assert _xp_for_level("unknown") == 100

    @pytest.mark.asyncio
    async def test_xp_earned_set_on_course_completion(self, mock_db, mock_user, mock_proposal, mock_company_user, mock_course):
        """xp_earned should be set on the ProposalCourse after completion."""
        mock_proposal.status = "accepted"
        mock_course.level = "advanced"

        pc = _make_proposal_course(mock_proposal.id, mock_course.id)

        filter_calls = []

        def side_effect_filter(*args, **kwargs):
            call_mock = MagicMock()
            filter_calls.append(call_mock)
            if len(filter_calls) == 1:
                call_mock.first.return_value = mock_proposal
            elif len(filter_calls) == 2:
                call_mock.first.return_value = pc
            elif len(filter_calls) == 3:
                call_mock.first.return_value = mock_course
            elif len(filter_calls) == 4:
                call_mock.all.return_value = [pc]
            elif len(filter_calls) == 5:
                call_mock.all.return_value = []
            elif len(filter_calls) == 6:
                call_mock.first.return_value = mock_company_user
            elif len(filter_calls) == 7:
                call_mock.first.return_value = mock_user
            elif len(filter_calls) == 8:
                call_mock.all.return_value = [pc]
            elif len(filter_calls) == 9:
                call_mock.all.return_value = [mock_course]
            else:
                call_mock.all.return_value = []
            return call_mock

        mock_db.query.return_value.filter.side_effect = side_effect_filter

        await complete_proposal_course(
            proposal_id=mock_proposal.id,
            course_id=mock_course.id,
            current_user=mock_user, db=mock_db,
        )
        assert pc.xp_earned == 300

    @pytest.mark.asyncio
    async def test_total_xp_accumulates(self, mock_db, mock_user, mock_proposal, mock_company_user, mock_course):
        """total_xp on proposal should accumulate as courses complete."""
        mock_proposal.status = "accepted"
        mock_proposal.total_xp = 100  # Already some XP

        pc = _make_proposal_course(mock_proposal.id, mock_course.id)

        filter_calls = []

        def side_effect_filter(*args, **kwargs):
            call_mock = MagicMock()
            filter_calls.append(call_mock)
            if len(filter_calls) == 1:
                call_mock.first.return_value = mock_proposal
            elif len(filter_calls) == 2:
                call_mock.first.return_value = pc
            elif len(filter_calls) == 3:
                call_mock.first.return_value = mock_course
            elif len(filter_calls) == 4:
                call_mock.all.return_value = [pc]
            elif len(filter_calls) == 5:
                call_mock.all.return_value = []
            elif len(filter_calls) == 6:
                call_mock.first.return_value = mock_company_user
            elif len(filter_calls) == 7:
                call_mock.first.return_value = mock_user
            elif len(filter_calls) == 8:
                call_mock.all.return_value = [pc]
            elif len(filter_calls) == 9:
                call_mock.all.return_value = [mock_course]
            else:
                call_mock.all.return_value = []
            return call_mock

        mock_db.query.return_value.filter.side_effect = side_effect_filter

        await complete_proposal_course(
            proposal_id=mock_proposal.id,
            course_id=mock_course.id,
            current_user=mock_user, db=mock_db,
        )
        # 100 existing + 200 (intermediate) + 50 (all_complete milestone for 1/1 = 100%)
        assert mock_proposal.total_xp > 100


# --- Gamification: Milestone creation ---


class TestMilestoneCreation:
    """Tests for milestone creation during course completion."""

    @pytest.mark.asyncio
    async def test_course_completed_milestone_created(self, mock_db, mock_user, mock_proposal, mock_company_user, mock_course):
        """A course_completed milestone should be created when a course is completed."""
        mock_proposal.status = "accepted"

        pc = _make_proposal_course(mock_proposal.id, mock_course.id)

        filter_calls = []

        def side_effect_filter(*args, **kwargs):
            call_mock = MagicMock()
            filter_calls.append(call_mock)
            if len(filter_calls) == 1:
                call_mock.first.return_value = mock_proposal
            elif len(filter_calls) == 2:
                call_mock.first.return_value = pc
            elif len(filter_calls) == 3:
                call_mock.first.return_value = mock_course
            elif len(filter_calls) == 4:
                call_mock.all.return_value = [pc]
            elif len(filter_calls) == 5:
                call_mock.all.return_value = []
            elif len(filter_calls) == 6:
                call_mock.first.return_value = mock_company_user
            elif len(filter_calls) == 7:
                call_mock.first.return_value = mock_user
            elif len(filter_calls) == 8:
                call_mock.all.return_value = [pc]
            elif len(filter_calls) == 9:
                call_mock.all.return_value = [mock_course]
            else:
                call_mock.all.return_value = []
            return call_mock

        mock_db.query.return_value.filter.side_effect = side_effect_filter

        await complete_proposal_course(
            proposal_id=mock_proposal.id,
            course_id=mock_course.id,
            current_user=mock_user, db=mock_db,
        )
        # db.add should be called for the milestone(s)
        add_calls = mock_db.add.call_args_list
        assert len(add_calls) >= 1  # At least 1 milestone added

    @pytest.mark.asyncio
    async def test_streak_3_milestone_created(self, mock_db, mock_user, mock_proposal, mock_company_user):
        """A streak_3 milestone should be created when 3 consecutive courses are completed."""
        mock_proposal.status = "accepted"
        mock_proposal.total_xp = 0

        c1 = _make_course(title="Course 1", level="beginner")
        c2 = _make_course(title="Course 2", level="beginner")
        c3 = _make_course(title="Course 3", level="beginner")

        pc1 = _make_proposal_course(mock_proposal.id, c1.id, order=0, is_completed=1, completed_at=datetime(2024, 7, 1, tzinfo=timezone.utc), xp_earned=100)
        pc2 = _make_proposal_course(mock_proposal.id, c2.id, order=1, is_completed=1, completed_at=datetime(2024, 7, 2, tzinfo=timezone.utc), xp_earned=100)
        pc3 = _make_proposal_course(mock_proposal.id, c3.id, order=2)

        filter_calls = []

        def side_effect_filter(*args, **kwargs):
            call_mock = MagicMock()
            filter_calls.append(call_mock)
            if len(filter_calls) == 1:
                call_mock.first.return_value = mock_proposal
            elif len(filter_calls) == 2:
                call_mock.first.return_value = pc3
            elif len(filter_calls) == 3:
                call_mock.first.return_value = c3
            elif len(filter_calls) == 4:
                call_mock.all.return_value = [pc1, pc2, pc3]
            elif len(filter_calls) == 5:
                call_mock.all.return_value = []  # no existing milestones
            elif len(filter_calls) == 6:
                call_mock.first.return_value = mock_company_user
            elif len(filter_calls) == 7:
                call_mock.first.return_value = mock_user
            elif len(filter_calls) == 8:
                call_mock.all.return_value = [pc1, pc2, pc3]
            elif len(filter_calls) == 9:
                call_mock.all.return_value = [c1, c2, c3]
            else:
                call_mock.all.return_value = []
            return call_mock

        mock_db.query.return_value.filter.side_effect = side_effect_filter

        await complete_proposal_course(
            proposal_id=mock_proposal.id,
            course_id=c3.id,
            current_user=mock_user, db=mock_db,
        )
        # XP should include streak_3 (100) + course_completed + all_complete (50)
        assert mock_proposal.total_xp >= 250

    @pytest.mark.asyncio
    async def test_progress_milestones_50_percent(self, mock_db, mock_user, mock_proposal, mock_company_user):
        """50% milestone should be created when half the courses are completed."""
        mock_proposal.status = "accepted"
        mock_proposal.total_xp = 0

        c1 = _make_course(title="Course 1", level="beginner")
        c2 = _make_course(title="Course 2", level="beginner")
        c3 = _make_course(title="Course 3", level="beginner")
        c4 = _make_course(title="Course 4", level="beginner")

        pc1 = _make_proposal_course(mock_proposal.id, c1.id, order=0, is_completed=1, xp_earned=100)
        pc2 = _make_proposal_course(mock_proposal.id, c2.id, order=1)
        pc3 = _make_proposal_course(mock_proposal.id, c3.id, order=2)
        pc4 = _make_proposal_course(mock_proposal.id, c4.id, order=3)

        filter_calls = []

        def side_effect_filter(*args, **kwargs):
            call_mock = MagicMock()
            filter_calls.append(call_mock)
            if len(filter_calls) == 1:
                call_mock.first.return_value = mock_proposal
            elif len(filter_calls) == 2:
                call_mock.first.return_value = pc2
            elif len(filter_calls) == 3:
                call_mock.first.return_value = c2
            elif len(filter_calls) == 4:
                call_mock.all.return_value = [pc1, pc2, pc3, pc4]
            elif len(filter_calls) == 5:
                call_mock.all.return_value = []  # no existing milestones
            elif len(filter_calls) == 6:
                call_mock.first.return_value = mock_company_user
            elif len(filter_calls) == 7:
                call_mock.first.return_value = mock_user
            elif len(filter_calls) == 8:
                call_mock.all.return_value = [pc1, pc2, pc3, pc4]
            elif len(filter_calls) == 9:
                call_mock.all.return_value = [c1, c2, c3, c4]
            else:
                call_mock.all.return_value = []
            return call_mock

        mock_db.query.return_value.filter.side_effect = side_effect_filter

        await complete_proposal_course(
            proposal_id=mock_proposal.id,
            course_id=c2.id,
            current_user=mock_user, db=mock_db,
        )
        # Should have course_completed + 25_percent + 50_percent milestones
        # 100 (course) + 50 (25%) + 50 (50%) = 200
        assert mock_proposal.total_xp == 200


# --- PATCH /proposals/{id}/courses/{course_id}/start ---


class TestStartProposalCourse:
    """Tests for the PATCH /proposals/{id}/courses/{course_id}/start endpoint."""

    @pytest.mark.asyncio
    async def test_start_course_success(self, mock_db, mock_user, mock_proposal, mock_proposal_course, mock_company_user, mock_course):
        """Talent should be able to start a course in an accepted proposal."""
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
                # all_pcs to check first course
                call_mock.all.return_value = [mock_proposal_course]
            elif len(filter_calls) == 4:
                call_mock.first.return_value = mock_company_user
            elif len(filter_calls) == 5:
                call_mock.first.return_value = mock_user
            elif len(filter_calls) == 6:
                call_mock.all.return_value = [mock_proposal_course]
            elif len(filter_calls) == 7:
                call_mock.all.return_value = [mock_course]
            else:
                call_mock.all.return_value = []
            return call_mock

        mock_db.query.return_value.filter.side_effect = side_effect_filter

        result = await start_proposal_course(
            proposal_id=mock_proposal.id,
            course_id=mock_course.id,
            current_user=mock_user, db=mock_db,
        )
        assert mock_proposal_course.started_at is not None

    @pytest.mark.asyncio
    async def test_start_course_already_started(self, mock_db, mock_user, mock_proposal, mock_proposal_course, mock_course):
        """Should raise 400 if course is already started."""
        mock_proposal.status = "accepted"
        mock_proposal_course.started_at = datetime(2024, 7, 1, tzinfo=timezone.utc)

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
            await start_proposal_course(
                proposal_id=mock_proposal.id,
                course_id=mock_course.id,
                current_user=mock_user, db=mock_db,
            )
        assert exc_info.value.status_code == 400
        assert "already started" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_start_course_wrong_user(self, mock_db, mock_proposal, mock_proposal_course, mock_course):
        """Non-recipient talent should get 403."""
        mock_proposal.status = "accepted"
        mock_db.query.return_value.filter.return_value.first.return_value = mock_proposal

        other_talent = MagicMock()
        other_talent.id = str(uuid4())
        other_talent.user_type = "talent"

        with pytest.raises(HTTPException) as exc_info:
            await start_proposal_course(
                proposal_id=mock_proposal.id,
                course_id=mock_course.id,
                current_user=other_talent, db=mock_db,
            )
        assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_start_course_wrong_status(self, mock_db, mock_user, mock_proposal, mock_course):
        """Should raise 400 when proposal is not accepted."""
        mock_proposal.status = "sent"
        mock_db.query.return_value.filter.return_value.first.return_value = mock_proposal

        with pytest.raises(HTTPException) as exc_info:
            await start_proposal_course(
                proposal_id=mock_proposal.id,
                course_id=mock_course.id,
                current_user=mock_user, db=mock_db,
            )
        assert exc_info.value.status_code == 400
        assert "must be accepted" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_start_course_company_rejected(self, mock_db, mock_company_user):
        """Company should not be able to start courses."""
        with pytest.raises(HTTPException) as exc_info:
            await start_proposal_course(
                proposal_id=str(uuid4()),
                course_id=str(uuid4()),
                current_user=mock_company_user, db=mock_db,
            )
        assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_first_course_milestone(self, mock_db, mock_user, mock_proposal, mock_proposal_course, mock_company_user, mock_course):
        """First course started should create first_course milestone (+25 XP)."""
        mock_proposal.status = "accepted"
        mock_proposal.total_xp = 0

        filter_calls = []

        def side_effect_filter(*args, **kwargs):
            call_mock = MagicMock()
            filter_calls.append(call_mock)
            if len(filter_calls) == 1:
                call_mock.first.return_value = mock_proposal
            elif len(filter_calls) == 2:
                call_mock.first.return_value = mock_proposal_course
            elif len(filter_calls) == 3:
                call_mock.all.return_value = [mock_proposal_course]
            elif len(filter_calls) == 4:
                call_mock.first.return_value = mock_company_user
            elif len(filter_calls) == 5:
                call_mock.first.return_value = mock_user
            elif len(filter_calls) == 6:
                call_mock.all.return_value = [mock_proposal_course]
            elif len(filter_calls) == 7:
                call_mock.all.return_value = [mock_course]
            else:
                call_mock.all.return_value = []
            return call_mock

        mock_db.query.return_value.filter.side_effect = side_effect_filter

        await start_proposal_course(
            proposal_id=mock_proposal.id,
            course_id=mock_course.id,
            current_user=mock_user, db=mock_db,
        )
        # 10 (course_started) + 25 (first_course) = 35
        assert mock_proposal.total_xp == 35

    @pytest.mark.asyncio
    async def test_second_course_no_first_course_milestone(self, mock_db, mock_user, mock_proposal, mock_company_user, mock_course):
        """Second course started should NOT create first_course milestone."""
        mock_proposal.status = "accepted"
        mock_proposal.total_xp = 35

        c2 = _make_course(title="Course 2")
        pc1 = _make_proposal_course(mock_proposal.id, mock_course.id, order=0, started_at=datetime(2024, 7, 1, tzinfo=timezone.utc))
        pc2 = _make_proposal_course(mock_proposal.id, c2.id, order=1)

        filter_calls = []

        def side_effect_filter(*args, **kwargs):
            call_mock = MagicMock()
            filter_calls.append(call_mock)
            if len(filter_calls) == 1:
                call_mock.first.return_value = mock_proposal
            elif len(filter_calls) == 2:
                call_mock.first.return_value = pc2
            elif len(filter_calls) == 3:
                call_mock.all.return_value = [pc1, pc2]
            elif len(filter_calls) == 4:
                call_mock.first.return_value = mock_company_user
            elif len(filter_calls) == 5:
                call_mock.first.return_value = mock_user
            elif len(filter_calls) == 6:
                call_mock.all.return_value = [pc1, pc2]
            elif len(filter_calls) == 7:
                call_mock.all.return_value = [mock_course, c2]
            else:
                call_mock.all.return_value = []
            return call_mock

        mock_db.query.return_value.filter.side_effect = side_effect_filter

        await start_proposal_course(
            proposal_id=mock_proposal.id,
            course_id=c2.id,
            current_user=mock_user, db=mock_db,
        )
        # Only 10 (course_started), NOT +25
        assert mock_proposal.total_xp == 45  # 35 + 10


# --- PATCH /proposals/{id}/courses/{course_id}/notes ---


class TestUpdateCourseNotes:
    """Tests for the PATCH /proposals/{id}/courses/{course_id}/notes endpoint."""

    @pytest.mark.asyncio
    async def test_talent_updates_notes_success(self, mock_db, mock_user, mock_proposal, mock_proposal_course, mock_company_user, mock_course):
        """Talent should be able to update notes on a course."""
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
                call_mock.first.return_value = mock_company_user
            elif len(filter_calls) == 4:
                call_mock.first.return_value = mock_user
            elif len(filter_calls) == 5:
                call_mock.all.return_value = [mock_proposal_course]
            elif len(filter_calls) == 6:
                call_mock.all.return_value = [mock_course]
            else:
                call_mock.all.return_value = []
            return call_mock

        mock_db.query.return_value.filter.side_effect = side_effect_filter

        data = CourseNotesUpdate(talent_notes="Making great progress!")
        result = await update_course_notes(
            proposal_id=mock_proposal.id,
            course_id=mock_course.id,
            data=data,
            current_user=mock_user, db=mock_db,
        )
        assert mock_proposal_course.talent_notes == "Making great progress!"

    @pytest.mark.asyncio
    async def test_company_cannot_update_talent_notes(self, mock_db, mock_company_user):
        """Company should not be able to update talent notes."""
        with pytest.raises(HTTPException) as exc_info:
            await update_course_notes(
                proposal_id=str(uuid4()),
                course_id=str(uuid4()),
                data=CourseNotesUpdate(talent_notes="Sneaky"),
                current_user=mock_company_user, db=mock_db,
            )
        assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_notes_wrong_recipient(self, mock_db, mock_proposal):
        """Non-recipient talent should get 403."""
        mock_db.query.return_value.filter.return_value.first.return_value = mock_proposal

        other_talent = MagicMock()
        other_talent.id = str(uuid4())
        other_talent.user_type = "talent"

        with pytest.raises(HTTPException) as exc_info:
            await update_course_notes(
                proposal_id=mock_proposal.id,
                course_id=str(uuid4()),
                data=CourseNotesUpdate(talent_notes="test"),
                current_user=other_talent, db=mock_db,
            )
        assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_notes_rejected_on_sent_status(self, mock_db, mock_user, mock_proposal):
        """Updating notes should be rejected when proposal status is 'sent'."""
        mock_proposal.status = "sent"
        mock_db.query.return_value.filter.return_value.first.return_value = mock_proposal

        with pytest.raises(HTTPException) as exc_info:
            await update_course_notes(
                proposal_id=mock_proposal.id,
                course_id=str(uuid4()),
                data=CourseNotesUpdate(talent_notes="test"),
                current_user=mock_user, db=mock_db,
            )
        assert exc_info.value.status_code == 400
        assert "accepted, completed, or hired" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_notes_rejected_on_rejected_status(self, mock_db, mock_user, mock_proposal):
        """Updating notes should be rejected when proposal status is 'rejected'."""
        mock_proposal.status = "rejected"
        mock_db.query.return_value.filter.return_value.first.return_value = mock_proposal

        with pytest.raises(HTTPException) as exc_info:
            await update_course_notes(
                proposal_id=mock_proposal.id,
                course_id=str(uuid4()),
                data=CourseNotesUpdate(talent_notes="test"),
                current_user=mock_user, db=mock_db,
            )
        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_notes_rejected_on_draft_status(self, mock_db, mock_user, mock_proposal):
        """Updating notes should be rejected when proposal status is 'draft'."""
        mock_proposal.status = "draft"
        mock_db.query.return_value.filter.return_value.first.return_value = mock_proposal

        with pytest.raises(HTTPException) as exc_info:
            await update_course_notes(
                proposal_id=mock_proposal.id,
                course_id=str(uuid4()),
                data=CourseNotesUpdate(talent_notes="test"),
                current_user=mock_user, db=mock_db,
            )
        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_notes_allowed_on_completed_status(self, mock_db, mock_user, mock_proposal, mock_proposal_course, mock_company_user, mock_course):
        """Updating notes should succeed when proposal status is 'completed'."""
        mock_proposal.status = "completed"

        filter_calls = []

        def side_effect_filter(*args, **kwargs):
            call_mock = MagicMock()
            filter_calls.append(call_mock)
            if len(filter_calls) == 1:
                call_mock.first.return_value = mock_proposal
            elif len(filter_calls) == 2:
                call_mock.first.return_value = mock_proposal_course
            elif len(filter_calls) == 3:
                call_mock.first.return_value = mock_company_user
            elif len(filter_calls) == 4:
                call_mock.first.return_value = mock_user
            elif len(filter_calls) == 5:
                call_mock.all.return_value = [mock_proposal_course]
            elif len(filter_calls) == 6:
                call_mock.all.return_value = [mock_course]
            else:
                call_mock.all.return_value = []
            return call_mock

        mock_db.query.return_value.filter.side_effect = side_effect_filter

        data = CourseNotesUpdate(talent_notes="Completed but adding retrospective notes")
        result = await update_course_notes(
            proposal_id=mock_proposal.id,
            course_id=mock_course.id,
            data=data,
            current_user=mock_user, db=mock_db,
        )
        assert mock_proposal_course.talent_notes == "Completed but adding retrospective notes"

    @pytest.mark.asyncio
    async def test_notes_allowed_on_hired_status(self, mock_db, mock_user, mock_proposal, mock_proposal_course, mock_company_user, mock_course):
        """Updating notes should succeed when proposal status is 'hired'."""
        mock_proposal.status = "hired"

        filter_calls = []

        def side_effect_filter(*args, **kwargs):
            call_mock = MagicMock()
            filter_calls.append(call_mock)
            if len(filter_calls) == 1:
                call_mock.first.return_value = mock_proposal
            elif len(filter_calls) == 2:
                call_mock.first.return_value = mock_proposal_course
            elif len(filter_calls) == 3:
                call_mock.first.return_value = mock_company_user
            elif len(filter_calls) == 4:
                call_mock.first.return_value = mock_user
            elif len(filter_calls) == 5:
                call_mock.all.return_value = [mock_proposal_course]
            elif len(filter_calls) == 6:
                call_mock.all.return_value = [mock_course]
            else:
                call_mock.all.return_value = []
            return call_mock

        mock_db.query.return_value.filter.side_effect = side_effect_filter

        data = CourseNotesUpdate(talent_notes="Post-hire notes")
        result = await update_course_notes(
            proposal_id=mock_proposal.id,
            course_id=mock_course.id,
            data=data,
            current_user=mock_user, db=mock_db,
        )
        assert mock_proposal_course.talent_notes == "Post-hire notes"


# --- PATCH /proposals/{id}/courses/{course_id}/company-update ---


class TestUpdateCourseCompany:
    """Tests for the PATCH /proposals/{id}/courses/{course_id}/company-update endpoint."""

    @pytest.mark.asyncio
    async def test_company_updates_notes_and_deadline(self, mock_db, mock_company_user, mock_proposal, mock_proposal_course, mock_user, mock_course):
        """Company should be able to update notes and deadline."""
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
                call_mock.first.return_value = mock_company_user
            elif len(filter_calls) == 4:
                call_mock.first.return_value = mock_user
            elif len(filter_calls) == 5:
                call_mock.all.return_value = [mock_proposal_course]
            elif len(filter_calls) == 6:
                call_mock.all.return_value = [mock_course]
            else:
                call_mock.all.return_value = []
            return call_mock

        mock_db.query.return_value.filter.side_effect = side_effect_filter

        deadline = datetime(2025, 3, 1, tzinfo=timezone.utc)
        data = CompanyCourseUpdate(company_notes="Focus on chapter 3", deadline=deadline)
        result = await update_course_company(
            proposal_id=mock_proposal.id,
            course_id=mock_course.id,
            data=data,
            current_user=mock_company_user, db=mock_db,
        )
        assert mock_proposal_course.company_notes == "Focus on chapter 3"
        assert mock_proposal_course.deadline == deadline

    @pytest.mark.asyncio
    async def test_talent_cannot_update_company_fields(self, mock_db, mock_user):
        """Talent should not be able to update company fields."""
        with pytest.raises(HTTPException) as exc_info:
            await update_course_company(
                proposal_id=str(uuid4()),
                course_id=str(uuid4()),
                data=CompanyCourseUpdate(company_notes="Sneaky"),
                current_user=mock_user, db=mock_db,
            )
        assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_company_update_wrong_owner(self, mock_db, mock_proposal):
        """Company that doesn't own the proposal should get 403."""
        mock_db.query.return_value.filter.return_value.first.return_value = mock_proposal

        other_company = MagicMock()
        other_company.id = str(uuid4())
        other_company.user_type = "company"

        with pytest.raises(HTTPException) as exc_info:
            await update_course_company(
                proposal_id=mock_proposal.id,
                course_id=str(uuid4()),
                data=CompanyCourseUpdate(company_notes="test"),
                current_user=other_company, db=mock_db,
            )
        assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_company_update_rejected_on_sent_status(self, mock_db, mock_company_user, mock_proposal):
        """Company update should be rejected when proposal status is 'sent'."""
        mock_proposal.status = "sent"
        mock_db.query.return_value.filter.return_value.first.return_value = mock_proposal

        with pytest.raises(HTTPException) as exc_info:
            await update_course_company(
                proposal_id=mock_proposal.id,
                course_id=str(uuid4()),
                data=CompanyCourseUpdate(company_notes="test"),
                current_user=mock_company_user, db=mock_db,
            )
        assert exc_info.value.status_code == 400
        assert "accepted, completed, or hired" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_company_update_rejected_on_rejected_status(self, mock_db, mock_company_user, mock_proposal):
        """Company update should be rejected when proposal status is 'rejected'."""
        mock_proposal.status = "rejected"
        mock_db.query.return_value.filter.return_value.first.return_value = mock_proposal

        with pytest.raises(HTTPException) as exc_info:
            await update_course_company(
                proposal_id=mock_proposal.id,
                course_id=str(uuid4()),
                data=CompanyCourseUpdate(company_notes="test"),
                current_user=mock_company_user, db=mock_db,
            )
        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_company_update_rejected_on_draft_status(self, mock_db, mock_company_user, mock_proposal):
        """Company update should be rejected when proposal status is 'draft'."""
        mock_proposal.status = "draft"
        mock_db.query.return_value.filter.return_value.first.return_value = mock_proposal

        with pytest.raises(HTTPException) as exc_info:
            await update_course_company(
                proposal_id=mock_proposal.id,
                course_id=str(uuid4()),
                data=CompanyCourseUpdate(company_notes="test"),
                current_user=mock_company_user, db=mock_db,
            )
        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_company_update_allowed_on_completed_status(self, mock_db, mock_company_user, mock_proposal, mock_proposal_course, mock_user, mock_course):
        """Company update should succeed when proposal status is 'completed'."""
        mock_proposal.status = "completed"

        filter_calls = []

        def side_effect_filter(*args, **kwargs):
            call_mock = MagicMock()
            filter_calls.append(call_mock)
            if len(filter_calls) == 1:
                call_mock.first.return_value = mock_proposal
            elif len(filter_calls) == 2:
                call_mock.first.return_value = mock_proposal_course
            elif len(filter_calls) == 3:
                call_mock.first.return_value = mock_company_user
            elif len(filter_calls) == 4:
                call_mock.first.return_value = mock_user
            elif len(filter_calls) == 5:
                call_mock.all.return_value = [mock_proposal_course]
            elif len(filter_calls) == 6:
                call_mock.all.return_value = [mock_course]
            else:
                call_mock.all.return_value = []
            return call_mock

        mock_db.query.return_value.filter.side_effect = side_effect_filter

        data = CompanyCourseUpdate(company_notes="Post-completion feedback")
        result = await update_course_company(
            proposal_id=mock_proposal.id,
            course_id=mock_course.id,
            data=data,
            current_user=mock_company_user, db=mock_db,
        )
        assert mock_proposal_course.company_notes == "Post-completion feedback"

    @pytest.mark.asyncio
    async def test_company_update_allowed_on_hired_status(self, mock_db, mock_company_user, mock_proposal, mock_proposal_course, mock_user, mock_course):
        """Company update should succeed when proposal status is 'hired'."""
        mock_proposal.status = "hired"

        filter_calls = []

        def side_effect_filter(*args, **kwargs):
            call_mock = MagicMock()
            filter_calls.append(call_mock)
            if len(filter_calls) == 1:
                call_mock.first.return_value = mock_proposal
            elif len(filter_calls) == 2:
                call_mock.first.return_value = mock_proposal_course
            elif len(filter_calls) == 3:
                call_mock.first.return_value = mock_company_user
            elif len(filter_calls) == 4:
                call_mock.first.return_value = mock_user
            elif len(filter_calls) == 5:
                call_mock.all.return_value = [mock_proposal_course]
            elif len(filter_calls) == 6:
                call_mock.all.return_value = [mock_course]
            else:
                call_mock.all.return_value = []
            return call_mock

        mock_db.query.return_value.filter.side_effect = side_effect_filter

        data = CompanyCourseUpdate(company_notes="Post-hire notes from company")
        result = await update_course_company(
            proposal_id=mock_proposal.id,
            course_id=mock_course.id,
            data=data,
            current_user=mock_company_user, db=mock_db,
        )
        assert mock_proposal_course.company_notes == "Post-hire notes from company"


# --- Hiring tests ---


class TestHireAfterTraining:
    """Tests for the hire status transition (Feature 4)."""

    @pytest.mark.asyncio
    async def test_hire_from_accepted(self, mock_db, mock_company_user, mock_proposal, mock_user, mock_course, mock_proposal_course):
        """Company should be able to hire from accepted status."""
        mock_proposal.status = "accepted"

        # The update_proposal route queries for proposal, then for talent (to update availability),
        # then for company (to get company_name), then _fetch_proposal_data
        filter_calls = []

        def side_effect_filter(*args, **kwargs):
            call_mock = MagicMock()
            filter_calls.append(call_mock)
            if len(filter_calls) == 1:
                # proposal lookup
                call_mock.first.return_value = mock_proposal
            elif len(filter_calls) == 2:
                # talent lookup (for hired update)
                call_mock.first.return_value = mock_user
            elif len(filter_calls) == 3:
                # company lookup (for company_name)
                call_mock.first.return_value = mock_company_user
            elif len(filter_calls) == 4:
                # _fetch: company
                call_mock.first.return_value = mock_company_user
            elif len(filter_calls) == 5:
                # _fetch: talent
                call_mock.first.return_value = mock_user
            elif len(filter_calls) == 6:
                # _fetch: proposal_courses
                call_mock.all.return_value = [mock_proposal_course]
            elif len(filter_calls) == 7:
                # _fetch: courses
                call_mock.all.return_value = [mock_course]
            else:
                # _fetch: milestones
                call_mock.all.return_value = []
            return call_mock

        mock_db.query.return_value.filter.side_effect = side_effect_filter

        data = ProposalUpdate(status="hired", hiring_notes="Excellent training completion")
        result = await update_proposal(
            proposal_id=mock_proposal.id, data=data,
            current_user=mock_company_user, db=mock_db,
        )
        assert mock_proposal.status == "hired"
        assert mock_proposal.hired_at is not None
        assert mock_proposal.hiring_notes == "Excellent training completion"
        assert mock_user.availability_status == "employed"
        assert mock_user.adopted_by_company == "TechFlow Italia"

    @pytest.mark.asyncio
    async def test_hire_from_completed(self, mock_db, mock_company_user, mock_proposal, mock_user, mock_course, mock_proposal_course):
        """Company should be able to hire from completed status."""
        mock_proposal.status = "completed"

        filter_calls = []

        def side_effect_filter(*args, **kwargs):
            call_mock = MagicMock()
            filter_calls.append(call_mock)
            if len(filter_calls) == 1:
                call_mock.first.return_value = mock_proposal
            elif len(filter_calls) == 2:
                call_mock.first.return_value = mock_user
            elif len(filter_calls) == 3:
                call_mock.first.return_value = mock_company_user
            elif len(filter_calls) == 4:
                call_mock.first.return_value = mock_company_user
            elif len(filter_calls) == 5:
                call_mock.first.return_value = mock_user
            elif len(filter_calls) == 6:
                call_mock.all.return_value = [mock_proposal_course]
            elif len(filter_calls) == 7:
                call_mock.all.return_value = [mock_course]
            else:
                call_mock.all.return_value = []
            return call_mock

        mock_db.query.return_value.filter.side_effect = side_effect_filter

        data = ProposalUpdate(status="hired")
        result = await update_proposal(
            proposal_id=mock_proposal.id, data=data,
            current_user=mock_company_user, db=mock_db,
        )
        assert mock_proposal.status == "hired"
        assert mock_proposal.hired_at is not None

    @pytest.mark.asyncio
    async def test_invalid_hire_from_draft(self, mock_db, mock_company_user, mock_proposal):
        """Should reject draft -> hired transition."""
        mock_proposal.status = "draft"
        mock_db.query.return_value.filter.return_value.first.return_value = mock_proposal

        data = ProposalUpdate(status="hired")

        with pytest.raises(HTTPException) as exc_info:
            await update_proposal(
                proposal_id=mock_proposal.id, data=data,
                current_user=mock_company_user, db=mock_db,
            )
        assert exc_info.value.status_code == 400
        assert "Invalid status transition" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_invalid_hire_from_sent(self, mock_db, mock_company_user, mock_proposal):
        """Should reject sent -> hired transition."""
        mock_proposal.status = "sent"
        mock_db.query.return_value.filter.return_value.first.return_value = mock_proposal

        data = ProposalUpdate(status="hired")

        with pytest.raises(HTTPException) as exc_info:
            await update_proposal(
                proposal_id=mock_proposal.id, data=data,
                current_user=mock_company_user, db=mock_db,
            )
        assert exc_info.value.status_code == 400
        assert "Invalid status transition" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_invalid_hire_from_rejected(self, mock_db, mock_company_user, mock_proposal):
        """Should reject rejected -> hired transition."""
        mock_proposal.status = "rejected"
        mock_db.query.return_value.filter.return_value.first.return_value = mock_proposal

        data = ProposalUpdate(status="hired")

        with pytest.raises(HTTPException) as exc_info:
            await update_proposal(
                proposal_id=mock_proposal.id, data=data,
                current_user=mock_company_user, db=mock_db,
            )
        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_invalid_hire_from_hired(self, mock_db, mock_company_user, mock_proposal):
        """Should reject hired -> hired transition."""
        mock_proposal.status = "hired"
        mock_db.query.return_value.filter.return_value.first.return_value = mock_proposal

        data = ProposalUpdate(status="hired")

        with pytest.raises(HTTPException) as exc_info:
            await update_proposal(
                proposal_id=mock_proposal.id, data=data,
                current_user=mock_company_user, db=mock_db,
            )
        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_hiring_notes_stored(self, mock_db, mock_company_user, mock_proposal, mock_user, mock_course, mock_proposal_course):
        """Hiring notes should be stored when provided."""
        mock_proposal.status = "accepted"

        filter_calls = []

        def side_effect_filter(*args, **kwargs):
            call_mock = MagicMock()
            filter_calls.append(call_mock)
            if len(filter_calls) == 1:
                call_mock.first.return_value = mock_proposal
            elif len(filter_calls) == 2:
                call_mock.first.return_value = mock_user
            elif len(filter_calls) == 3:
                call_mock.first.return_value = mock_company_user
            elif len(filter_calls) == 4:
                call_mock.first.return_value = mock_company_user
            elif len(filter_calls) == 5:
                call_mock.first.return_value = mock_user
            elif len(filter_calls) == 6:
                call_mock.all.return_value = [mock_proposal_course]
            elif len(filter_calls) == 7:
                call_mock.all.return_value = [mock_course]
            else:
                call_mock.all.return_value = []
            return call_mock

        mock_db.query.return_value.filter.side_effect = side_effect_filter

        data = ProposalUpdate(status="hired", hiring_notes="Superb candidate, hired immediately")
        result = await update_proposal(
            proposal_id=mock_proposal.id, data=data,
            current_user=mock_company_user, db=mock_db,
        )
        assert mock_proposal.hiring_notes == "Superb candidate, hired immediately"

    @pytest.mark.asyncio
    async def test_hired_at_timestamp_set(self, mock_db, mock_company_user, mock_proposal, mock_user, mock_course, mock_proposal_course):
        """hired_at should be set when transitioning to hired."""
        mock_proposal.status = "completed"
        mock_proposal.hired_at = None

        filter_calls = []

        def side_effect_filter(*args, **kwargs):
            call_mock = MagicMock()
            filter_calls.append(call_mock)
            if len(filter_calls) == 1:
                call_mock.first.return_value = mock_proposal
            elif len(filter_calls) == 2:
                call_mock.first.return_value = mock_user
            elif len(filter_calls) == 3:
                call_mock.first.return_value = mock_company_user
            elif len(filter_calls) == 4:
                call_mock.first.return_value = mock_company_user
            elif len(filter_calls) == 5:
                call_mock.first.return_value = mock_user
            elif len(filter_calls) == 6:
                call_mock.all.return_value = [mock_proposal_course]
            elif len(filter_calls) == 7:
                call_mock.all.return_value = [mock_course]
            else:
                call_mock.all.return_value = []
            return call_mock

        mock_db.query.return_value.filter.side_effect = side_effect_filter

        data = ProposalUpdate(status="hired")
        result = await update_proposal(
            proposal_id=mock_proposal.id, data=data,
            current_user=mock_company_user, db=mock_db,
        )
        assert mock_proposal.hired_at is not None


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

        data = ProposalUpdate()

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

        data = ProposalUpdate(status="sent", message="sneaky update")

        with pytest.raises(HTTPException) as exc_info:
            await update_proposal(
                proposal_id=mock_proposal.id, data=data,
                current_user=mock_company_user, db=mock_db,
            )
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


# --- ProposalUpdate schema validation ---


class TestProposalUpdateSchema:
    """Tests for ProposalUpdate schema validation."""

    def test_hiring_notes_accepted(self):
        """ProposalUpdate should accept hiring_notes field."""
        data = ProposalUpdate(status="hired", hiring_notes="Great candidate")
        assert data.hiring_notes == "Great candidate"

    def test_hired_status_accepted(self):
        """ProposalUpdate should accept 'hired' status."""
        data = ProposalUpdate(status="hired")
        assert data.status == "hired"

    def test_invalid_status_rejected(self):
        """ProposalUpdate should reject invalid status values."""
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            ProposalUpdate(status="invalid_status")
