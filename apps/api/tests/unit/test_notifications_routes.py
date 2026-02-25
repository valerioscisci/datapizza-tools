"""Tests for notification route handlers (api/routes/notifications/).

Covers all 8 endpoints: GET emails, GET email by id, PATCH read,
PATCH read-all, GET unread-count, GET/PATCH preferences, POST daily-digest.
Uses importlib.import_module + patch.object for mocking (learning #23).
"""

from __future__ import annotations

import importlib
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import HTTPException

# Import the actual router module using importlib (learning #23)
_router_module = importlib.import_module("api.routes.notifications.router")

list_emails = _router_module.list_emails
get_email = _router_module.get_email
mark_email_read = _router_module.mark_email_read
mark_all_emails_read = _router_module.mark_all_emails_read
get_unread_count = _router_module.get_unread_count
get_preferences = _router_module.get_preferences
update_preferences = _router_module.update_preferences
trigger_daily_digest = _router_module.trigger_daily_digest


# --- Helpers ---


def _make_email(email_id=None, recipient_id=None, email_type="proposal_received",
                is_read=0, subject="Test Subject"):
    """Create a mock EmailLog."""
    e = MagicMock()
    e.id = email_id or str(uuid4())
    e.recipient_id = recipient_id or str(uuid4())
    e.recipient_email = "test@email.it"
    e.sender_label = "Datapizza"
    e.email_type = email_type
    e.subject = subject
    e.body_html = "<p>Test</p>"
    e.body_text = "Test"
    e.related_proposal_id = None
    e.is_read = is_read
    e.created_at = datetime(2024, 8, 1, tzinfo=timezone.utc)
    return e


def _make_pref(user_id, email_notifications=1, daily_digest=1, channel="email"):
    """Create a mock NotificationPreference."""
    pref = MagicMock()
    pref.id = str(uuid4())
    pref.user_id = user_id
    pref.email_notifications = email_notifications
    pref.daily_digest = daily_digest
    pref.channel = channel
    return pref


def _setup_db_for_emails(mock_db, items=None, total=0, unread_count=0):
    """Configure mock_db for list_emails endpoint."""
    from api.database.models import EmailLog as ELModel

    email_query = MagicMock()
    email_query.filter.return_value = email_query
    email_query.count.return_value = total
    email_query.order_by.return_value.offset.return_value.limit.return_value.all.return_value = items or []

    unread_query = MagicMock()
    unread_query.filter.return_value.count.return_value = unread_count

    call_count = [0]

    def query_side_effect(model):
        if model is ELModel:
            call_count[0] += 1
            if call_count[0] == 1:
                return email_query
            return unread_query
        return MagicMock()

    mock_db.query.side_effect = query_side_effect


# --- GET /notifications/emails ---


class TestListEmails:
    """Tests for the GET /notifications/emails endpoint."""

    @pytest.mark.asyncio
    async def test_returns_users_emails(self, mock_db, mock_user):
        """Should return emails for the current user."""
        email1 = _make_email(recipient_id=mock_user.id)
        email2 = _make_email(recipient_id=mock_user.id, email_type="daily_digest")

        _setup_db_for_emails(mock_db, items=[email1, email2], total=2, unread_count=1)

        result = await list_emails(
            page=1, page_size=20, email_type=None, is_read=None,
            current_user=mock_user, db=mock_db,
        )

        assert result.total == 2
        assert len(result.items) == 2
        assert result.page == 1
        assert result.page_size == 20
        assert result.unread_count == 1

    @pytest.mark.asyncio
    async def test_pagination(self, mock_db, mock_user):
        """Should respect pagination parameters."""
        _setup_db_for_emails(mock_db, items=[], total=50, unread_count=10)

        result = await list_emails(
            page=3, page_size=10, email_type=None, is_read=None,
            current_user=mock_user, db=mock_db,
        )

        assert result.total == 50
        assert result.page == 3
        assert result.page_size == 10

    @pytest.mark.asyncio
    async def test_filter_by_type(self, mock_db, mock_user):
        """Should filter by email_type."""
        email = _make_email(recipient_id=mock_user.id, email_type="daily_digest")
        _setup_db_for_emails(mock_db, items=[email], total=1, unread_count=0)

        result = await list_emails(
            page=1, page_size=20, email_type=["daily_digest"], is_read=None,
            current_user=mock_user, db=mock_db,
        )

        assert result.total == 1

    @pytest.mark.asyncio
    async def test_filter_by_read_status(self, mock_db, mock_user):
        """Should filter by is_read status."""
        _setup_db_for_emails(mock_db, items=[], total=0, unread_count=0)

        result = await list_emails(
            page=1, page_size=20, email_type=None, is_read=True,
            current_user=mock_user, db=mock_db,
        )

        assert result.total == 0


# --- GET /notifications/emails/{email_id} ---


class TestGetEmail:
    """Tests for the GET /notifications/emails/{email_id} endpoint."""

    @pytest.mark.asyncio
    async def test_returns_email_and_marks_read(self, mock_db, mock_user):
        """Should return the email and auto-mark it as read."""
        email = _make_email(recipient_id=mock_user.id, is_read=0)

        from api.database.models import EmailLog as ELModel
        mock_db.query.return_value.filter.return_value.first.return_value = email

        result = await get_email(email_id=email.id, current_user=mock_user, db=mock_db)

        assert result.id == email.id
        assert email.is_read == 1
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_already_read_email(self, mock_db, mock_user):
        """Should return already-read email without re-committing read status."""
        email = _make_email(recipient_id=mock_user.id, is_read=1)

        mock_db.query.return_value.filter.return_value.first.return_value = email

        result = await get_email(email_id=email.id, current_user=mock_user, db=mock_db)

        assert result.id == email.id
        mock_db.commit.assert_not_called()

    @pytest.mark.asyncio
    async def test_404_when_not_found(self, mock_db, mock_user):
        """Should raise 404 when email doesn't exist."""
        mock_db.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            await get_email(email_id="nonexistent", current_user=mock_user, db=mock_db)
        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_404_for_wrong_user(self, mock_db, mock_user):
        """Should raise 404 when email belongs to a different user (query scoped)."""
        mock_db.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            await get_email(email_id=str(uuid4()), current_user=mock_user, db=mock_db)
        assert exc_info.value.status_code == 404


# --- PATCH /notifications/emails/{email_id}/read ---


class TestMarkEmailRead:
    """Tests for the PATCH /notifications/emails/{email_id}/read endpoint."""

    @pytest.mark.asyncio
    async def test_marks_as_read(self, mock_db, mock_user):
        """Should mark a single email as read."""
        email = _make_email(recipient_id=mock_user.id, is_read=0)
        mock_db.query.return_value.filter.return_value.first.return_value = email

        result = await mark_email_read(email_id=email.id, current_user=mock_user, db=mock_db)

        assert result == {"ok": True}
        assert email.is_read == 1
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_404_when_not_found(self, mock_db, mock_user):
        """Should raise 404 when email not found."""
        mock_db.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            await mark_email_read(email_id="nonexistent", current_user=mock_user, db=mock_db)
        assert exc_info.value.status_code == 404


# --- PATCH /notifications/emails/read-all ---


class TestMarkAllEmailsRead:
    """Tests for the PATCH /notifications/emails/read-all endpoint."""

    @pytest.mark.asyncio
    async def test_marks_all_as_read(self, mock_db, mock_user):
        """Should mark all unread emails as read."""
        mock_db.query.return_value.filter.return_value.update.return_value = 5

        result = await mark_all_emails_read(current_user=mock_user, db=mock_db)

        assert result == {"ok": True, "count": 5}
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_returns_zero_when_no_unread(self, mock_db, mock_user):
        """Should return count 0 when all emails are already read."""
        mock_db.query.return_value.filter.return_value.update.return_value = 0

        result = await mark_all_emails_read(current_user=mock_user, db=mock_db)

        assert result == {"ok": True, "count": 0}


# --- GET /notifications/unread-count ---


class TestGetUnreadCount:
    """Tests for the GET /notifications/unread-count endpoint."""

    @pytest.mark.asyncio
    async def test_returns_correct_count(self, mock_db, mock_user):
        """Should return the count of unread emails."""
        mock_db.query.return_value.filter.return_value.count.return_value = 3

        result = await get_unread_count(current_user=mock_user, db=mock_db)

        assert result == {"count": 3}

    @pytest.mark.asyncio
    async def test_returns_zero_when_all_read(self, mock_db, mock_user):
        """Should return 0 when no unread emails."""
        mock_db.query.return_value.filter.return_value.count.return_value = 0

        result = await get_unread_count(current_user=mock_user, db=mock_db)

        assert result == {"count": 0}


# --- GET /notifications/preferences ---


class TestGetPreferences:
    """Tests for the GET /notifications/preferences endpoint."""

    @pytest.mark.asyncio
    async def test_returns_defaults_when_no_record(self, mock_db, mock_user):
        """Should return all-true defaults when no NotificationPreference exists."""
        mock_db.query.return_value.filter.return_value.first.return_value = None

        result = await get_preferences(current_user=mock_user, db=mock_db)

        assert result.email_notifications is True
        assert result.daily_digest is True
        assert result.channel == "email"

    @pytest.mark.asyncio
    async def test_returns_saved_preferences(self, mock_db, mock_user):
        """Should return saved preferences when record exists."""
        pref = _make_pref(mock_user.id, email_notifications=0, daily_digest=1, channel="telegram")
        mock_db.query.return_value.filter.return_value.first.return_value = pref

        result = await get_preferences(current_user=mock_user, db=mock_db)

        assert result.email_notifications is False
        assert result.daily_digest is True
        assert result.channel == "telegram"


# --- PATCH /notifications/preferences ---


class TestUpdatePreferences:
    """Tests for the PATCH /notifications/preferences endpoint."""

    @pytest.mark.asyncio
    async def test_creates_record_when_none_exists(self, mock_db, mock_user):
        """Should create a new preference record when none exists."""
        from api.routes.notifications.schemas import NotificationPreferenceUpdate

        mock_db.query.return_value.filter.return_value.first.return_value = None

        data = NotificationPreferenceUpdate(email_notifications=False)

        result = await update_preferences(data=data, current_user=mock_user, db=mock_db)

        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        assert result.email_notifications is False

    @pytest.mark.asyncio
    async def test_updates_existing_record(self, mock_db, mock_user):
        """Should update an existing preference record."""
        from api.routes.notifications.schemas import NotificationPreferenceUpdate

        pref = _make_pref(mock_user.id, email_notifications=1, daily_digest=1)
        mock_db.query.return_value.filter.return_value.first.return_value = pref

        data = NotificationPreferenceUpdate(daily_digest=False, channel="telegram")

        result = await update_preferences(data=data, current_user=mock_user, db=mock_db)

        assert pref.daily_digest == 0
        assert pref.channel == "telegram"
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_partial_update(self, mock_db, mock_user):
        """Should only update provided fields."""
        from api.routes.notifications.schemas import NotificationPreferenceUpdate

        pref = _make_pref(mock_user.id, email_notifications=1, daily_digest=1, channel="email")
        mock_db.query.return_value.filter.return_value.first.return_value = pref

        data = NotificationPreferenceUpdate(channel="telegram")

        result = await update_preferences(data=data, current_user=mock_user, db=mock_db)

        # email_notifications and daily_digest should remain unchanged
        assert pref.email_notifications == 1
        assert pref.daily_digest == 1
        assert pref.channel == "telegram"


# --- POST /notifications/daily-digest ---


class TestTriggerDailyDigest:
    """Tests for the POST /notifications/daily-digest endpoint."""

    @pytest.mark.asyncio
    async def test_generates_digest(self, mock_db, mock_user):
        """Should generate a daily digest email."""
        digest_email = _make_email(
            recipient_id=mock_user.id,
            email_type="daily_digest",
            subject="Il tuo digest giornaliero — Datapizza",
        )

        with patch.object(_router_module, "EmailService") as mock_service:
            mock_service.generate_daily_digest.return_value = digest_email

            result = await trigger_daily_digest(current_user=mock_user, db=mock_db)

        assert result.email_type == "daily_digest"
        mock_service.generate_daily_digest.assert_called_once_with(mock_db, mock_user)

    @pytest.mark.asyncio
    async def test_returns_message_when_disabled(self, mock_db, mock_user):
        """Should return message when daily digest is disabled."""
        with patch.object(_router_module, "EmailService") as mock_service:
            mock_service.generate_daily_digest.return_value = None

            result = await trigger_daily_digest(current_user=mock_user, db=mock_db)

        assert result == {"message": "Daily digest disabled"}


# --- Schema validation tests ---


class TestNotificationSchemas:
    """Tests for notification Pydantic schemas."""

    def test_email_log_response_valid(self):
        """Should create a valid EmailLogResponse."""
        from api.routes.notifications.schemas import EmailLogResponse

        now = datetime.now(timezone.utc)
        resp = EmailLogResponse(
            id="abc",
            recipient_email="test@email.it",
            sender_label="Datapizza",
            email_type="proposal_received",
            subject="Test",
            body_html="<p>Test</p>",
            is_read=False,
            created_at=now,
        )
        assert resp.id == "abc"
        assert resp.is_read is False

    def test_email_log_list_response(self):
        """Should create a valid EmailLogListResponse."""
        from api.routes.notifications.schemas import EmailLogListResponse, EmailLogResponse

        now = datetime.now(timezone.utc)
        resp = EmailLogListResponse(
            items=[
                EmailLogResponse(
                    id="abc", recipient_email="test@email.it",
                    sender_label="Datapizza", email_type="daily_digest",
                    subject="Test", body_html="<p>Test</p>",
                    is_read=True, created_at=now,
                )
            ],
            total=1, page=1, page_size=20, unread_count=0,
        )
        assert resp.total == 1
        assert resp.unread_count == 0

    def test_notification_preference_response(self):
        """Should create a valid NotificationPreferenceResponse."""
        from api.routes.notifications.schemas import NotificationPreferenceResponse

        resp = NotificationPreferenceResponse(
            email_notifications=True,
            daily_digest=False,
            channel="telegram",
        )
        assert resp.email_notifications is True
        assert resp.daily_digest is False
        assert resp.channel == "telegram"

    def test_notification_preference_update_partial(self):
        """Should allow partial updates."""
        from api.routes.notifications.schemas import NotificationPreferenceUpdate

        data = NotificationPreferenceUpdate(email_notifications=False)
        assert data.email_notifications is False
        assert data.daily_digest is None
        assert data.channel is None

    def test_notification_preference_update_all_fields(self):
        """Should accept all fields."""
        from api.routes.notifications.schemas import NotificationPreferenceUpdate

        data = NotificationPreferenceUpdate(
            email_notifications=True,
            daily_digest=False,
            channel="telegram",
        )
        assert data.email_notifications is True
        assert data.daily_digest is False
        assert data.channel == "telegram"
