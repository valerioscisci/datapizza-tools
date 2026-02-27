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
trigger_bulk_daily_digest = _router_module.trigger_bulk_daily_digest
link_telegram = _router_module.link_telegram
unlink_telegram = _router_module.unlink_telegram
telegram_webhook = _router_module.telegram_webhook


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


def _make_pref(user_id, email_notifications=1, daily_digest=1, channel="email",
               telegram_chat_id=None, telegram_notifications=0):
    """Create a mock NotificationPreference."""
    pref = MagicMock()
    pref.id = str(uuid4())
    pref.user_id = user_id
    pref.email_notifications = email_notifications
    pref.daily_digest = daily_digest
    pref.channel = channel
    pref.telegram_chat_id = telegram_chat_id
    pref.telegram_notifications = telegram_notifications
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
        assert result.telegram_chat_id is None
        assert result.telegram_notifications is False

    @pytest.mark.asyncio
    async def test_returns_saved_preferences(self, mock_db, mock_user):
        """Should return saved preferences when record exists."""
        pref = _make_pref(mock_user.id, email_notifications=0, daily_digest=1, channel="telegram",
                          telegram_chat_id="12345", telegram_notifications=1)
        mock_db.query.return_value.filter.return_value.first.return_value = pref

        result = await get_preferences(current_user=mock_user, db=mock_db)

        assert result.email_notifications is False
        assert result.daily_digest is True
        assert result.channel == "telegram"
        assert result.telegram_chat_id == "12345"
        assert result.telegram_notifications is True


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


# --- POST /notifications/daily-digest/bulk ---


def _make_mock_request(api_key=None):
    """Create a mock Request with optional X-API-Key header."""
    request = MagicMock()
    headers = {}
    if api_key is not None:
        headers["X-API-Key"] = api_key
    request.headers = headers
    return request


class TestTriggerBulkDailyDigest:
    """Tests for the POST /notifications/daily-digest/bulk endpoint."""

    @pytest.mark.asyncio
    async def test_missing_cron_api_key_returns_503(self, mock_db):
        """Should return 503 when CRON_API_KEY env var is not set."""
        request = _make_mock_request(api_key="any-key")

        with patch.object(_router_module, "os") as mock_os:
            mock_os.getenv.return_value = None

            with pytest.raises(HTTPException) as exc_info:
                await trigger_bulk_daily_digest(request=request, db=mock_db)

        assert exc_info.value.status_code == 503
        assert "not configured" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_invalid_api_key_returns_401(self, mock_db):
        """Should return 401 when the provided API key doesn't match."""
        request = _make_mock_request(api_key="wrong-key")

        with patch.object(_router_module, "os") as mock_os:
            mock_os.getenv.return_value = "correct-key"

            with pytest.raises(HTTPException) as exc_info:
                await trigger_bulk_daily_digest(request=request, db=mock_db)

        assert exc_info.value.status_code == 401
        assert "Invalid API key" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_missing_api_key_header_returns_401(self, mock_db):
        """Should return 401 when X-API-Key header is missing entirely."""
        request = _make_mock_request(api_key=None)
        request.headers = {}  # No X-API-Key

        with patch.object(_router_module, "os") as mock_os:
            mock_os.getenv.return_value = "correct-key"

            with pytest.raises(HTTPException) as exc_info:
                await trigger_bulk_daily_digest(request=request, db=mock_db)

        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_sends_digest_to_opted_in_users(self, mock_db):
        """Should send digest to users with daily_digest enabled."""
        from api.database.models import NotificationPreference as NPModel
        from api.database.models import User as UModel

        user1 = MagicMock()
        user1.id = "user-1"
        user1.is_active = 1
        user2 = MagicMock()
        user2.id = "user-2"
        user2.is_active = 1

        pref1 = MagicMock()
        pref1.user_id = "user-1"
        pref1.daily_digest = 1
        pref2 = MagicMock()
        pref2.user_id = "user-2"
        pref2.daily_digest = 1

        digest_email = _make_email(email_type="daily_digest")

        call_count = [0]

        def query_side_effect(model):
            call_count[0] += 1
            q = MagicMock()
            if model is NPModel:
                q.filter.return_value.all.return_value = [pref1, pref2]
            elif model is UModel:
                q.filter.return_value.all.return_value = [user1, user2]
            return q

        mock_db.query.side_effect = query_side_effect

        request = _make_mock_request(api_key="valid-key")

        with patch.object(_router_module, "os") as mock_os, \
             patch.object(_router_module, "EmailService") as mock_service:
            mock_os.getenv.return_value = "valid-key"
            mock_service.generate_daily_digest.return_value = digest_email

            result = await trigger_bulk_daily_digest(request=request, db=mock_db)

        assert result.sent == 2
        assert result.failed == 0
        assert result.total == 2
        assert mock_service.generate_daily_digest.call_count == 2

    @pytest.mark.asyncio
    async def test_includes_users_without_preferences(self, mock_db):
        """Should include users who have no NotificationPreference record (default=True)."""
        from api.database.models import NotificationPreference as NPModel
        from api.database.models import User as UModel

        user1 = MagicMock()
        user1.id = "user-with-pref"
        user1.is_active = 1
        user2 = MagicMock()
        user2.id = "user-without-pref"
        user2.is_active = 1

        pref1 = MagicMock()
        pref1.user_id = "user-with-pref"
        pref1.daily_digest = 1

        digest_email = _make_email(email_type="daily_digest")

        def query_side_effect(model):
            q = MagicMock()
            if model is NPModel:
                q.filter.return_value.all.return_value = [pref1]
            elif model is UModel:
                q.filter.return_value.all.return_value = [user1, user2]
            return q

        mock_db.query.side_effect = query_side_effect

        request = _make_mock_request(api_key="valid-key")

        with patch.object(_router_module, "os") as mock_os, \
             patch.object(_router_module, "EmailService") as mock_service:
            mock_os.getenv.return_value = "valid-key"
            mock_service.generate_daily_digest.return_value = digest_email

            result = await trigger_bulk_daily_digest(request=request, db=mock_db)

        # Both users should be processed (one with pref, one without)
        assert result.total == 2
        assert result.sent == 2
        assert mock_service.generate_daily_digest.call_count == 2

    @pytest.mark.asyncio
    async def test_one_user_fails_continues_with_others(self, mock_db):
        """Should continue processing when one user fails."""
        from api.database.models import NotificationPreference as NPModel
        from api.database.models import User as UModel

        user1 = MagicMock()
        user1.id = "user-fail"
        user1.is_active = 1
        user2 = MagicMock()
        user2.id = "user-success"
        user2.is_active = 1

        pref1 = MagicMock()
        pref1.user_id = "user-fail"
        pref1.daily_digest = 1
        pref2 = MagicMock()
        pref2.user_id = "user-success"
        pref2.daily_digest = 1

        digest_email = _make_email(email_type="daily_digest")

        def query_side_effect(model):
            q = MagicMock()
            if model is NPModel:
                q.filter.return_value.all.return_value = [pref1, pref2]
            elif model is UModel:
                q.filter.return_value.all.return_value = [user1, user2]
            return q

        mock_db.query.side_effect = query_side_effect

        call_count = [0]

        def digest_side_effect(db, user):
            call_count[0] += 1
            if user.id == "user-fail":
                raise RuntimeError("AI service unavailable")
            return digest_email

        request = _make_mock_request(api_key="valid-key")

        with patch.object(_router_module, "os") as mock_os, \
             patch.object(_router_module, "EmailService") as mock_service:
            mock_os.getenv.return_value = "valid-key"
            mock_service.generate_daily_digest.side_effect = digest_side_effect

            result = await trigger_bulk_daily_digest(request=request, db=mock_db)

        assert result.sent == 1
        assert result.failed == 1
        assert result.total == 2
        assert len(result.errors) == 1
        assert result.errors[0].user_id == "user-fail"
        assert "AI service unavailable" in result.errors[0].error

    @pytest.mark.asyncio
    async def test_skipped_when_digest_returns_none(self, mock_db):
        """Should count as skipped when generate_daily_digest returns None."""
        from api.database.models import NotificationPreference as NPModel
        from api.database.models import User as UModel

        user1 = MagicMock()
        user1.id = "user-skipped"
        user1.is_active = 1

        pref1 = MagicMock()
        pref1.user_id = "user-skipped"
        pref1.daily_digest = 1

        def query_side_effect(model):
            q = MagicMock()
            if model is NPModel:
                q.filter.return_value.all.return_value = [pref1]
            elif model is UModel:
                q.filter.return_value.all.return_value = [user1]
            return q

        mock_db.query.side_effect = query_side_effect

        request = _make_mock_request(api_key="valid-key")

        with patch.object(_router_module, "os") as mock_os, \
             patch.object(_router_module, "EmailService") as mock_service:
            mock_os.getenv.return_value = "valid-key"
            mock_service.generate_daily_digest.return_value = None

            result = await trigger_bulk_daily_digest(request=request, db=mock_db)

        assert result.sent == 0
        assert result.skipped == 1
        assert result.total == 1

    @pytest.mark.asyncio
    async def test_no_users_returns_zero_totals(self, mock_db):
        """Should return all zeros when no users have digest enabled."""
        from api.database.models import NotificationPreference as NPModel
        from api.database.models import User as UModel

        def query_side_effect(model):
            q = MagicMock()
            if model is NPModel:
                q.filter.return_value.all.return_value = []
            elif model is UModel:
                q.filter.return_value.all.return_value = []
            return q

        mock_db.query.side_effect = query_side_effect

        request = _make_mock_request(api_key="valid-key")

        with patch.object(_router_module, "os") as mock_os:
            mock_os.getenv.return_value = "valid-key"

            result = await trigger_bulk_daily_digest(request=request, db=mock_db)

        assert result.sent == 0
        assert result.skipped == 0
        assert result.failed == 0
        assert result.total == 0


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
            telegram_chat_id="12345",
            telegram_notifications=True,
        )
        assert resp.email_notifications is True
        assert resp.daily_digest is False
        assert resp.channel == "telegram"
        assert resp.telegram_chat_id == "12345"
        assert resp.telegram_notifications is True

    def test_notification_preference_response_defaults(self):
        """Should use defaults for optional telegram fields."""
        from api.routes.notifications.schemas import NotificationPreferenceResponse

        resp = NotificationPreferenceResponse(
            email_notifications=True,
            daily_digest=True,
            channel="email",
        )
        assert resp.telegram_chat_id is None
        assert resp.telegram_notifications is False

    def test_notification_preference_update_partial(self):
        """Should allow partial updates."""
        from api.routes.notifications.schemas import NotificationPreferenceUpdate

        data = NotificationPreferenceUpdate(email_notifications=False)
        assert data.email_notifications is False
        assert data.daily_digest is None
        assert data.channel is None
        assert data.telegram_notifications is None

    def test_notification_preference_update_all_fields(self):
        """Should accept all fields."""
        from api.routes.notifications.schemas import NotificationPreferenceUpdate

        data = NotificationPreferenceUpdate(
            email_notifications=True,
            daily_digest=False,
            channel="both",
            telegram_notifications=True,
        )
        assert data.email_notifications is True
        assert data.daily_digest is False
        assert data.channel == "both"
        assert data.telegram_notifications is True

    def test_notification_preference_update_invalid_channel(self):
        """Should reject invalid channel values."""
        from api.routes.notifications.schemas import NotificationPreferenceUpdate
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            NotificationPreferenceUpdate(channel="sms")

    def test_telegram_update_with_start_command(self):
        """Should parse a valid /start update."""
        from api.routes.notifications.schemas import TelegramUpdate, TelegramMessage, TelegramChat

        update = TelegramUpdate(
            update_id=123,
            message=TelegramMessage(chat=TelegramChat(id=99887766), text="/start"),
        )
        assert update.message is not None
        assert update.message.chat.id == 99887766
        assert update.message.text == "/start"

    def test_telegram_update_without_message(self):
        """Should accept update without message field."""
        from api.routes.notifications.schemas import TelegramUpdate

        update = TelegramUpdate(update_id=124)
        assert update.message is None

    def test_telegram_update_message_without_text(self):
        """Should accept message without text."""
        from api.routes.notifications.schemas import TelegramUpdate, TelegramMessage, TelegramChat

        update = TelegramUpdate(
            update_id=125,
            message=TelegramMessage(chat=TelegramChat(id=99887766)),
        )
        assert update.message is not None
        assert update.message.text is None

    def test_bulk_digest_response(self):
        """Should create a valid BulkDigestResponse."""
        from api.routes.notifications.schemas import BulkDigestResponse

        resp = BulkDigestResponse(sent=5, skipped=2, failed=1, total=8)
        assert resp.sent == 5
        assert resp.skipped == 2
        assert resp.failed == 1
        assert resp.total == 8
        assert resp.errors == []

    def test_bulk_digest_response_with_errors(self):
        """Should accept errors list in BulkDigestResponse."""
        from api.routes.notifications.schemas import BulkDigestError, BulkDigestResponse

        errors = [BulkDigestError(user_id="u1", error="Failed")]
        resp = BulkDigestResponse(sent=0, skipped=0, failed=1, total=1, errors=errors)
        assert len(resp.errors) == 1
        assert resp.errors[0].user_id == "u1"
        assert resp.errors[0].error == "Failed"

    def test_telegram_link_request(self):
        """Should create a valid TelegramLinkRequest."""
        from api.routes.notifications.schemas import TelegramLinkRequest

        req = TelegramLinkRequest(chat_id="123456789")
        assert req.chat_id == "123456789"

    def test_telegram_link_request_negative_chat_id(self):
        """Should accept negative chat_id (group chats)."""
        from api.routes.notifications.schemas import TelegramLinkRequest

        req = TelegramLinkRequest(chat_id="-100123456789")
        assert req.chat_id == "-100123456789"

    def test_telegram_link_request_rejects_empty(self):
        """Should reject empty chat_id."""
        from api.routes.notifications.schemas import TelegramLinkRequest
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            TelegramLinkRequest(chat_id="")

    def test_telegram_link_request_rejects_non_numeric(self):
        """Should reject non-numeric chat_id."""
        from api.routes.notifications.schemas import TelegramLinkRequest
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            TelegramLinkRequest(chat_id="abc_not_a_number")

    def test_telegram_link_request_rejects_too_long(self):
        """Should reject chat_id longer than 50 characters."""
        from api.routes.notifications.schemas import TelegramLinkRequest
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            TelegramLinkRequest(chat_id="1" * 51)


# --- POST /notifications/telegram/link ---


class TestLinkTelegram:
    """Tests for the POST /notifications/telegram/link endpoint."""

    @pytest.mark.asyncio
    async def test_link_creates_pref_when_none_exists(self, mock_db, mock_user):
        """Should create a new preference record with telegram linked."""
        from api.routes.notifications.schemas import TelegramLinkRequest

        mock_db.query.return_value.filter.return_value.first.return_value = None

        data = TelegramLinkRequest(chat_id="123456789")

        result = await link_telegram(data=data, current_user=mock_user, db=mock_db)

        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        assert result.telegram_chat_id == "123456789"
        assert result.telegram_notifications is True

    @pytest.mark.asyncio
    async def test_link_updates_existing_pref(self, mock_db, mock_user):
        """Should update existing preference with telegram chat_id."""
        from api.routes.notifications.schemas import TelegramLinkRequest

        pref = _make_pref(mock_user.id, telegram_chat_id=None, telegram_notifications=0)
        mock_db.query.return_value.filter.return_value.first.return_value = pref

        data = TelegramLinkRequest(chat_id="987654321")

        result = await link_telegram(data=data, current_user=mock_user, db=mock_db)

        assert pref.telegram_chat_id == "987654321"
        assert pref.telegram_notifications == 1
        mock_db.commit.assert_called_once()


# --- DELETE /notifications/telegram/link ---


class TestUnlinkTelegram:
    """Tests for the DELETE /notifications/telegram/link endpoint."""

    @pytest.mark.asyncio
    async def test_unlink_removes_telegram(self, mock_db, mock_user):
        """Should remove telegram_chat_id and disable telegram_notifications."""
        pref = _make_pref(mock_user.id, telegram_chat_id="123456789", telegram_notifications=1)
        mock_db.query.return_value.filter.return_value.first.return_value = pref

        result = await unlink_telegram(current_user=mock_user, db=mock_db)

        assert pref.telegram_chat_id is None
        assert pref.telegram_notifications == 0
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_unlink_returns_defaults_when_no_pref(self, mock_db, mock_user):
        """Should return defaults when no preference record exists."""
        mock_db.query.return_value.filter.return_value.first.return_value = None

        result = await unlink_telegram(current_user=mock_user, db=mock_db)

        assert result.telegram_chat_id is None
        assert result.telegram_notifications is False
        assert result.email_notifications is True


# --- POST /notifications/telegram/webhook ---


class TestTelegramWebhook:
    """Tests for the POST /notifications/telegram/webhook endpoint."""

    @pytest.mark.asyncio
    async def test_start_command_replies_with_chat_id(self):
        """Should reply with chat ID when /start is received."""
        from api.routes.notifications.schemas import TelegramUpdate, TelegramMessage, TelegramChat

        update = TelegramUpdate(
            update_id=123,
            message=TelegramMessage(chat=TelegramChat(id=99887766), text="/start"),
        )
        mock_request = MagicMock()
        mock_request.headers = {}

        with patch.object(_router_module, "TelegramService") as mock_tg, \
             patch.object(_router_module, "os") as mock_os:
            mock_os.getenv.return_value = None
            result = await telegram_webhook(update=update, request=mock_request)

        assert result == {"ok": True}
        mock_tg.send_message.assert_called_once()
        call_args = mock_tg.send_message.call_args
        assert call_args[0][0] == "99887766"
        assert "99887766" in call_args[0][1]

    @pytest.mark.asyncio
    async def test_start_with_botname_replies(self):
        """Should reply when /start@botname is received."""
        from api.routes.notifications.schemas import TelegramUpdate, TelegramMessage, TelegramChat

        update = TelegramUpdate(
            update_id=130,
            message=TelegramMessage(chat=TelegramChat(id=99887766), text="/start@datapizza_notify_bot"),
        )
        mock_request = MagicMock()
        mock_request.headers = {}

        with patch.object(_router_module, "TelegramService") as mock_tg, \
             patch.object(_router_module, "os") as mock_os:
            mock_os.getenv.return_value = None
            result = await telegram_webhook(update=update, request=mock_request)

        assert result == {"ok": True}
        mock_tg.send_message.assert_called_once()

    @pytest.mark.asyncio
    async def test_ignores_non_start_messages(self):
        """Should return OK but not reply for non-/start messages."""
        from api.routes.notifications.schemas import TelegramUpdate, TelegramMessage, TelegramChat

        update = TelegramUpdate(
            update_id=124,
            message=TelegramMessage(chat=TelegramChat(id=99887766), text="hello"),
        )
        mock_request = MagicMock()
        mock_request.headers = {}

        with patch.object(_router_module, "TelegramService") as mock_tg, \
             patch.object(_router_module, "os") as mock_os:
            mock_os.getenv.return_value = None
            result = await telegram_webhook(update=update, request=mock_request)

        assert result == {"ok": True}
        mock_tg.send_message.assert_not_called()

    @pytest.mark.asyncio
    async def test_handles_update_without_message(self):
        """Should return OK for updates without message."""
        from api.routes.notifications.schemas import TelegramUpdate

        update = TelegramUpdate(update_id=125)
        mock_request = MagicMock()
        mock_request.headers = {}

        with patch.object(_router_module, "TelegramService") as mock_tg, \
             patch.object(_router_module, "os") as mock_os:
            mock_os.getenv.return_value = None
            result = await telegram_webhook(update=update, request=mock_request)

        assert result == {"ok": True}
        mock_tg.send_message.assert_not_called()

    @pytest.mark.asyncio
    async def test_handles_message_without_text(self):
        """Should return OK for messages without text (e.g., photos)."""
        from api.routes.notifications.schemas import TelegramUpdate, TelegramMessage, TelegramChat

        update = TelegramUpdate(
            update_id=126,
            message=TelegramMessage(chat=TelegramChat(id=99887766)),
        )
        mock_request = MagicMock()
        mock_request.headers = {}

        with patch.object(_router_module, "TelegramService") as mock_tg, \
             patch.object(_router_module, "os") as mock_os:
            mock_os.getenv.return_value = None
            result = await telegram_webhook(update=update, request=mock_request)

        assert result == {"ok": True}
        mock_tg.send_message.assert_not_called()

    @pytest.mark.asyncio
    async def test_valid_secret_token_allows_request(self):
        """Should process request when secret token matches."""
        from api.routes.notifications.schemas import TelegramUpdate, TelegramMessage, TelegramChat

        update = TelegramUpdate(
            update_id=127,
            message=TelegramMessage(chat=TelegramChat(id=99887766), text="/start"),
        )
        mock_request = MagicMock()
        mock_request.headers = {"X-Telegram-Bot-Api-Secret-Token": "my-secret-123"}

        with patch.object(_router_module, "TelegramService") as mock_tg, \
             patch.object(_router_module, "os") as mock_os:
            mock_os.getenv.return_value = "my-secret-123"
            result = await telegram_webhook(update=update, request=mock_request)

        assert result == {"ok": True}
        mock_tg.send_message.assert_called_once()

    @pytest.mark.asyncio
    async def test_invalid_secret_token_rejects_silently(self):
        """Should return OK but not process when secret token mismatches."""
        from api.routes.notifications.schemas import TelegramUpdate, TelegramMessage, TelegramChat

        update = TelegramUpdate(
            update_id=128,
            message=TelegramMessage(chat=TelegramChat(id=99887766), text="/start"),
        )
        mock_request = MagicMock()
        mock_request.headers = {"X-Telegram-Bot-Api-Secret-Token": "wrong-secret"}

        with patch.object(_router_module, "TelegramService") as mock_tg, \
             patch.object(_router_module, "os") as mock_os:
            mock_os.getenv.return_value = "correct-secret"
            result = await telegram_webhook(update=update, request=mock_request)

        assert result == {"ok": True}
        mock_tg.send_message.assert_not_called()

    @pytest.mark.asyncio
    async def test_no_secret_configured_allows_all(self):
        """Should process all requests when no secret is configured."""
        from api.routes.notifications.schemas import TelegramUpdate, TelegramMessage, TelegramChat

        update = TelegramUpdate(
            update_id=129,
            message=TelegramMessage(chat=TelegramChat(id=99887766), text="/start"),
        )
        mock_request = MagicMock()
        mock_request.headers = {}

        with patch.object(_router_module, "TelegramService") as mock_tg, \
             patch.object(_router_module, "os") as mock_os:
            mock_os.getenv.return_value = None
            result = await telegram_webhook(update=update, request=mock_request)

        assert result == {"ok": True}
        mock_tg.send_message.assert_called_once()
