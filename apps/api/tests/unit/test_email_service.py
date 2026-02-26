"""Tests for the EmailService (api/services/email_service.py).

Covers: send_email, all send_* methods, generate_daily_digest,
preference checking, and edge cases.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from unittest.mock import MagicMock, call
from uuid import uuid4

import pytest


# --- Helpers ---


def _make_user(user_id=None, email="test@email.it", full_name="Test User",
               user_type="talent", company_name=None):
    """Create a mock User."""
    user = MagicMock()
    user.id = user_id or str(uuid4())
    user.email = email
    user.full_name = full_name
    user.user_type = user_type
    user.company_name = company_name
    return user


def _make_pref(user_id, email_notifications=1, daily_digest=1, channel="email"):
    """Create a mock NotificationPreference."""
    pref = MagicMock()
    pref.id = str(uuid4())
    pref.user_id = user_id
    pref.email_notifications = email_notifications
    pref.daily_digest = daily_digest
    pref.channel = channel
    return pref


def _make_proposal(proposal_id=None, company_id=None, talent_id=None,
                   budget_range="5000-8000", total_xp=100):
    """Create a mock Proposal."""
    p = MagicMock()
    p.id = proposal_id or str(uuid4())
    p.company_id = company_id or str(uuid4())
    p.talent_id = talent_id or str(uuid4())
    p.budget_range = budget_range
    p.total_xp = total_xp
    return p


def _make_course(title="AI Fundamentals", provider="Coursera", level="beginner"):
    """Create a mock Course."""
    c = MagicMock()
    c.id = str(uuid4())
    c.title = title
    c.provider = provider
    c.level = level
    c.is_active = 1
    c.created_at = datetime(2024, 6, 1, tzinfo=timezone.utc)
    return c


def _make_cache(user_id, content, cache_type="career_advice"):
    """Create a mock AICache."""
    cache = MagicMock()
    cache.id = str(uuid4())
    cache.user_id = user_id
    cache.cache_type = cache_type
    cache.content_json = json.dumps(content, ensure_ascii=False)
    return cache


def _setup_db_for_send_email(mock_db, user=None, pref=None):
    """Configure mock_db for send_email calls."""
    from api.database.models import User as UserModel, NotificationPreference as NPModel

    user_query = MagicMock()
    user_query.filter.return_value.first.return_value = user

    pref_query = MagicMock()
    pref_query.filter.return_value.first.return_value = pref

    def query_side_effect(model):
        if model is UserModel:
            return user_query
        elif model is NPModel:
            return pref_query
        return MagicMock()

    mock_db.query.side_effect = query_side_effect


def _setup_db_for_digest(mock_db, user=None, pref=None, cache=None, courses=None):
    """Configure mock_db for generate_daily_digest calls."""
    from api.database.models import (
        User as UserModel,
        NotificationPreference as NPModel,
        AICache as AICacheModel,
        Course as CourseModel,
    )

    user_query = MagicMock()
    user_query.filter.return_value.first.return_value = user

    pref_query = MagicMock()
    pref_query.filter.return_value.first.return_value = pref

    cache_query = MagicMock()
    cache_query.filter.return_value.first.return_value = cache

    course_query = MagicMock()
    course_query.filter.return_value.order_by.return_value.limit.return_value.all.return_value = courses or []

    def query_side_effect(model):
        if model is UserModel:
            return user_query
        elif model is NPModel:
            return pref_query
        elif model is AICacheModel:
            return cache_query
        elif model is CourseModel:
            return course_query
        return MagicMock()

    mock_db.query.side_effect = query_side_effect


# --- Tests ---


class TestSendEmail:
    """Tests for EmailService.send_email."""

    def test_creates_email_log_when_enabled(self, mock_db):
        """Should create an EmailLog when notifications are enabled."""
        from api.services.email_service import EmailService

        user = _make_user()
        _setup_db_for_send_email(mock_db, user=user, pref=None)  # No pref = default enabled

        result = EmailService.send_email(
            mock_db, user.id, "proposal_received",
            "Test Subject", "<p>Test</p>",
        )

        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()
        # Result is the EmailLog object that was added
        added = mock_db.add.call_args[0][0]
        assert added.email_type == "proposal_received"
        assert added.recipient_id == user.id
        assert added.recipient_email == user.email

    def test_returns_none_when_notifications_disabled(self, mock_db):
        """Should return None when email_notifications is disabled."""
        from api.services.email_service import EmailService

        user = _make_user()
        pref = _make_pref(user.id, email_notifications=0)
        _setup_db_for_send_email(mock_db, user=user, pref=pref)

        result = EmailService.send_email(
            mock_db, user.id, "proposal_received",
            "Test Subject", "<p>Test</p>",
        )

        assert result is None
        mock_db.add.assert_not_called()

    def test_returns_none_when_user_not_found(self, mock_db):
        """Should return None when recipient user doesn't exist."""
        from api.services.email_service import EmailService

        _setup_db_for_send_email(mock_db, user=None, pref=None)

        result = EmailService.send_email(
            mock_db, "nonexistent", "proposal_received",
            "Test Subject", "<p>Test</p>",
        )

        assert result is None
        mock_db.add.assert_not_called()

    def test_uses_default_preferences_when_no_record(self, mock_db):
        """Should default to enabled when no NotificationPreference exists."""
        from api.services.email_service import EmailService

        user = _make_user()
        _setup_db_for_send_email(mock_db, user=user, pref=None)

        result = EmailService.send_email(
            mock_db, user.id, "daily_digest",
            "Digest", "<p>Digest</p>",
        )

        mock_db.add.assert_called_once()

    def test_sets_related_proposal_id(self, mock_db):
        """Should set related_proposal_id on the EmailLog."""
        from api.services.email_service import EmailService

        user = _make_user()
        proposal_id = str(uuid4())
        _setup_db_for_send_email(mock_db, user=user, pref=None)

        EmailService.send_email(
            mock_db, user.id, "proposal_received",
            "Test", "<p>Test</p>", related_proposal_id=proposal_id,
        )

        added = mock_db.add.call_args[0][0]
        assert added.related_proposal_id == proposal_id

    def test_sets_sender_label(self, mock_db):
        """Should use custom sender label."""
        from api.services.email_service import EmailService

        user = _make_user()
        _setup_db_for_send_email(mock_db, user=user, pref=None)

        EmailService.send_email(
            mock_db, user.id, "proposal_received",
            "Test", "<p>Test</p>", sender_label="Custom Sender",
        )

        added = mock_db.add.call_args[0][0]
        assert added.sender_label == "Custom Sender"


class TestSendProposalReceived:
    """Tests for EmailService.send_proposal_received."""

    def test_sends_to_talent(self, mock_db):
        """Should send proposal_received email to talent."""
        from api.services.email_service import EmailService

        talent = _make_user(email="talent@email.it", full_name="Marco Rossi")
        company = _make_user(user_type="company", company_name="TechFlow Italia", full_name="Laura Verdi")
        proposal = _make_proposal(talent_id=talent.id, company_id=company.id)

        _setup_db_for_send_email(mock_db, user=talent, pref=None)

        EmailService.send_proposal_received(mock_db, proposal, talent, company)

        added = mock_db.add.call_args[0][0]
        assert added.email_type == "proposal_received"
        assert added.recipient_id == talent.id
        assert "TechFlow Italia" in added.subject


class TestSendProposalAccepted:
    """Tests for EmailService.send_proposal_accepted."""

    def test_sends_to_company(self, mock_db):
        """Should send proposal_accepted email to company."""
        from api.services.email_service import EmailService

        talent = _make_user(full_name="Marco Rossi")
        company = _make_user(user_type="company", company_name="TechFlow Italia", full_name="Laura Verdi")
        proposal = _make_proposal()

        _setup_db_for_send_email(mock_db, user=company, pref=None)

        EmailService.send_proposal_accepted(mock_db, proposal, talent, company)

        added = mock_db.add.call_args[0][0]
        assert added.email_type == "proposal_accepted"
        assert added.recipient_id == company.id
        assert "Marco Rossi" in added.subject


class TestSendProposalRejected:
    """Tests for EmailService.send_proposal_rejected."""

    def test_sends_to_company(self, mock_db):
        """Should send proposal_rejected email to company."""
        from api.services.email_service import EmailService

        talent = _make_user(full_name="Marco Rossi")
        company = _make_user(user_type="company", full_name="Laura Verdi")
        proposal = _make_proposal()

        _setup_db_for_send_email(mock_db, user=company, pref=None)

        EmailService.send_proposal_rejected(mock_db, proposal, talent, company)

        added = mock_db.add.call_args[0][0]
        assert added.email_type == "proposal_rejected"
        assert added.recipient_id == company.id


class TestSendCourseStarted:
    """Tests for EmailService.send_course_started."""

    def test_sends_to_company(self, mock_db):
        """Should send course_started email to company."""
        from api.services.email_service import EmailService

        talent = _make_user(full_name="Marco Rossi")
        company = _make_user(user_type="company", full_name="Laura Verdi")
        proposal = _make_proposal()

        _setup_db_for_send_email(mock_db, user=company, pref=None)

        EmailService.send_course_started(mock_db, proposal, "AI Fundamentals", talent, company)

        added = mock_db.add.call_args[0][0]
        assert added.email_type == "course_started"
        assert "AI Fundamentals" in added.subject


class TestSendCourseCompleted:
    """Tests for EmailService.send_course_completed."""

    def test_sends_to_company(self, mock_db):
        """Should send course_completed email to company."""
        from api.services.email_service import EmailService

        talent = _make_user(full_name="Marco Rossi")
        company = _make_user(user_type="company", full_name="Laura Verdi")
        proposal = _make_proposal()

        _setup_db_for_send_email(mock_db, user=company, pref=None)

        EmailService.send_course_completed(mock_db, proposal, "AI Fundamentals", talent, company)

        added = mock_db.add.call_args[0][0]
        assert added.email_type == "course_completed"
        assert "AI Fundamentals" in added.subject


class TestSendMilestoneReached:
    """Tests for EmailService.send_milestone_reached."""

    def test_sends_to_talent(self, mock_db):
        """Should send milestone_reached email to talent."""
        from api.services.email_service import EmailService

        talent = _make_user(full_name="Marco Rossi")
        proposal = _make_proposal(total_xp=300)

        _setup_db_for_send_email(mock_db, user=talent, pref=None)

        EmailService.send_milestone_reached(mock_db, proposal, "course_completed", 200, talent)

        added = mock_db.add.call_args[0][0]
        assert added.email_type == "milestone_reached"
        assert "+200 XP" in added.subject


class TestSendHiringConfirmation:
    """Tests for EmailService.send_hiring_confirmation."""

    def test_sends_to_both(self, mock_db):
        """Should create 2 emails: one for talent and one for company."""
        from api.services.email_service import EmailService

        talent = _make_user(email="talent@email.it", full_name="Marco Rossi")
        company = _make_user(email="company@email.it", user_type="company",
                             company_name="TechFlow", full_name="Laura Verdi")
        proposal = _make_proposal(talent_id=talent.id, company_id=company.id)

        # We need to handle 2 send_email calls, each needing the right user lookup
        from api.database.models import User as UserModel, NotificationPreference as NPModel

        call_count = [0]

        def query_side_effect(model):
            q = MagicMock()
            if model is UserModel:
                # First call looks up talent, second looks up company
                if call_count[0] == 0:
                    q.filter.return_value.first.return_value = talent
                else:
                    q.filter.return_value.first.return_value = company
                call_count[0] += 1
            elif model is NPModel:
                q.filter.return_value.first.return_value = None  # defaults
            return q

        mock_db.query.side_effect = query_side_effect

        results = EmailService.send_hiring_confirmation(mock_db, proposal, talent, company)

        assert len(results) == 2
        assert mock_db.add.call_count == 2
        # Verify both emails are hiring_confirmation type
        for c in mock_db.add.call_args_list:
            added = c[0][0]
            assert added.email_type == "hiring_confirmation"


class TestGenerateDailyDigest:
    """Tests for EmailService.generate_daily_digest."""

    def test_creates_digest_with_cache(self, mock_db):
        """Should generate digest using cached career advice."""
        from api.services.email_service import EmailService

        user = _make_user(full_name="Marco Rossi")
        cache_content = {
            "career_direction": "AI Engineer",
            "recommended_courses": [{"course_id": "c1", "reason": "Perfect"}],
            "skill_gaps": ["Docker"],
        }
        cache = _make_cache(user.id, cache_content)

        _setup_db_for_digest(mock_db, user=user, pref=None, cache=cache)

        EmailService.generate_daily_digest(mock_db, user)

        added = mock_db.add.call_args[0][0]
        assert added.email_type == "daily_digest"
        assert "digest giornaliero" in added.subject

    def test_falls_back_to_recent_courses(self, mock_db):
        """Should fall back to recent courses when no cache exists."""
        from api.services.email_service import EmailService

        user = _make_user(full_name="Marco Rossi")
        courses = [_make_course(title=f"Course {i}") for i in range(3)]

        _setup_db_for_digest(mock_db, user=user, pref=None, cache=None, courses=courses)

        EmailService.generate_daily_digest(mock_db, user)

        added = mock_db.add.call_args[0][0]
        assert added.email_type == "daily_digest"
        assert "Course 0" in added.body_html

    def test_returns_none_when_disabled(self, mock_db):
        """Should return None when daily_digest preference is disabled."""
        from api.services.email_service import EmailService

        user = _make_user()
        pref = _make_pref(user.id, daily_digest=0)

        _setup_db_for_digest(mock_db, user=user, pref=pref)

        result = EmailService.generate_daily_digest(mock_db, user)

        assert result is None
        mock_db.add.assert_not_called()

    def test_creates_digest_when_no_courses(self, mock_db):
        """Should create digest even with no courses (shows fallback message)."""
        from api.services.email_service import EmailService

        user = _make_user(full_name="Marco Rossi")

        _setup_db_for_digest(mock_db, user=user, pref=None, cache=None, courses=[])

        EmailService.generate_daily_digest(mock_db, user)

        added = mock_db.add.call_args[0][0]
        assert added.email_type == "daily_digest"
        assert "Nessun corso disponibile" in added.body_html

    def test_handles_malformed_cache_json(self, mock_db):
        """Should fall back to courses when cache JSON is malformed."""
        from api.services.email_service import EmailService

        user = _make_user(full_name="Marco Rossi")
        cache = MagicMock()
        cache.content_json = "not valid json"
        cache.cache_type = "career_advice"
        courses = [_make_course()]

        _setup_db_for_digest(mock_db, user=user, pref=None, cache=cache, courses=courses)

        EmailService.generate_daily_digest(mock_db, user)

        added = mock_db.add.call_args[0][0]
        # Should fall back to course suggestions
        assert "Corsi in evidenza" in added.body_html
