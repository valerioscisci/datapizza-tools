"""Tests for the TelegramService (api/services/telegram_service.py).

Covers: send_message success/failure, send_notification with telegram
enabled/disabled, missing bot token, and link/unlink flow.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest


# --- Helpers ---


def _make_pref(user_id, telegram_chat_id=None, telegram_notifications=0):
    """Create a mock NotificationPreference."""
    pref = MagicMock()
    pref.id = str(uuid4())
    pref.user_id = user_id
    pref.email_notifications = 1
    pref.daily_digest = 1
    pref.channel = "email"
    pref.telegram_chat_id = telegram_chat_id
    pref.telegram_notifications = telegram_notifications
    return pref


# --- Tests ---


class TestSendMessage:
    """Tests for TelegramService.send_message."""

    @patch("api.services.telegram_service.TelegramService._get_bot_token")
    @patch("api.services.telegram_service.httpx.Client")
    def test_send_message_success(self, mock_client_cls, mock_get_token):
        """Should return True on successful message send."""
        from api.services.telegram_service import TelegramService

        mock_get_token.return_value = "test-bot-token"
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.post.return_value = mock_response
        mock_client_cls.return_value = mock_client

        result = TelegramService.send_message("12345", "Hello!")

        assert result is True
        mock_client.post.assert_called_once()
        call_args = mock_client.post.call_args
        assert "12345" in str(call_args)

    @patch("api.services.telegram_service.TelegramService._get_bot_token")
    @patch("api.services.telegram_service.httpx.Client")
    def test_send_message_api_error(self, mock_client_cls, mock_get_token):
        """Should return False when Telegram API returns an error."""
        from api.services.telegram_service import TelegramService

        mock_get_token.return_value = "test-bot-token"
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.post.return_value = mock_response
        mock_client_cls.return_value = mock_client

        result = TelegramService.send_message("12345", "Hello!")

        assert result is False

    @patch("api.services.telegram_service.TelegramService._get_bot_token")
    def test_send_message_no_token(self, mock_get_token):
        """Should return False when bot token is not set."""
        from api.services.telegram_service import TelegramService

        mock_get_token.return_value = None

        result = TelegramService.send_message("12345", "Hello!")

        assert result is False

    @patch("api.services.telegram_service.TelegramService._get_bot_token")
    @patch("api.services.telegram_service.httpx.Client")
    def test_send_message_network_error(self, mock_client_cls, mock_get_token):
        """Should return False on network error."""
        from api.services.telegram_service import TelegramService

        mock_get_token.return_value = "test-bot-token"
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.post.side_effect = Exception("Connection timeout")
        mock_client_cls.return_value = mock_client

        result = TelegramService.send_message("12345", "Hello!")

        assert result is False


class TestSendNotification:
    """Tests for TelegramService.send_notification."""

    def test_sends_when_telegram_enabled(self, mock_db):
        """Should send notification when telegram is enabled and chat_id is set."""
        from api.services.telegram_service import TelegramService

        user_id = str(uuid4())
        pref = _make_pref(user_id, telegram_chat_id="12345", telegram_notifications=1)

        from api.database.models import NotificationPreference as NPModel
        mock_db.query.return_value.filter.return_value.first.return_value = pref

        with patch.object(TelegramService, "send_message", return_value=True) as mock_send:
            result = TelegramService.send_notification(mock_db, user_id, "Test message")

        assert result is True
        mock_send.assert_called_once_with("12345", "Test message")

    def test_skips_when_telegram_disabled(self, mock_db):
        """Should return False when telegram_notifications is disabled."""
        from api.services.telegram_service import TelegramService

        user_id = str(uuid4())
        pref = _make_pref(user_id, telegram_chat_id="12345", telegram_notifications=0)
        mock_db.query.return_value.filter.return_value.first.return_value = pref

        with patch.object(TelegramService, "send_message") as mock_send:
            result = TelegramService.send_notification(mock_db, user_id, "Test message")

        assert result is False
        mock_send.assert_not_called()

    def test_skips_when_no_chat_id(self, mock_db):
        """Should return False when telegram_chat_id is not set."""
        from api.services.telegram_service import TelegramService

        user_id = str(uuid4())
        pref = _make_pref(user_id, telegram_chat_id=None, telegram_notifications=1)
        mock_db.query.return_value.filter.return_value.first.return_value = pref

        with patch.object(TelegramService, "send_message") as mock_send:
            result = TelegramService.send_notification(mock_db, user_id, "Test message")

        assert result is False
        mock_send.assert_not_called()

    def test_skips_when_no_pref(self, mock_db):
        """Should return False when no preference record exists."""
        from api.services.telegram_service import TelegramService

        mock_db.query.return_value.filter.return_value.first.return_value = None

        with patch.object(TelegramService, "send_message") as mock_send:
            result = TelegramService.send_notification(mock_db, str(uuid4()), "Test")

        assert result is False
        mock_send.assert_not_called()

    def test_send_failure_returns_false(self, mock_db):
        """Should return False when send_message fails."""
        from api.services.telegram_service import TelegramService

        user_id = str(uuid4())
        pref = _make_pref(user_id, telegram_chat_id="12345", telegram_notifications=1)
        mock_db.query.return_value.filter.return_value.first.return_value = pref

        with patch.object(TelegramService, "send_message", return_value=False) as mock_send:
            result = TelegramService.send_notification(mock_db, user_id, "Test message")

        assert result is False
        mock_send.assert_called_once()


class TestSetWebhook:
    """Tests for TelegramService.set_webhook."""

    @patch("api.services.telegram_service.TelegramService._get_bot_token")
    @patch("api.services.telegram_service.httpx.Client")
    def test_set_webhook_success(self, mock_client_cls, mock_get_token):
        """Should return True on successful webhook registration."""
        from api.services.telegram_service import TelegramService

        mock_get_token.return_value = "test-token"
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"ok": True}
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.post.return_value = mock_response
        mock_client_cls.return_value = mock_client

        result = TelegramService.set_webhook("https://example.com/webhook")
        assert result is True

    @patch("api.services.telegram_service.TelegramService._get_bot_token")
    @patch("api.services.telegram_service.httpx.Client")
    def test_set_webhook_with_secret(self, mock_client_cls, mock_get_token):
        """Should include secret_token in payload when provided."""
        from api.services.telegram_service import TelegramService

        mock_get_token.return_value = "test-token"
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"ok": True}
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.post.return_value = mock_response
        mock_client_cls.return_value = mock_client

        result = TelegramService.set_webhook("https://example.com/webhook", "my-secret")
        assert result is True
        call_payload = mock_client.post.call_args[1]["json"]
        assert call_payload["secret_token"] == "my-secret"

    @patch("api.services.telegram_service.TelegramService._get_bot_token")
    def test_set_webhook_no_token(self, mock_get_token):
        """Should return False when bot token is not set."""
        from api.services.telegram_service import TelegramService

        mock_get_token.return_value = None
        result = TelegramService.set_webhook("https://example.com/webhook")
        assert result is False

    @patch("api.services.telegram_service.TelegramService._get_bot_token")
    @patch("api.services.telegram_service.httpx.Client")
    def test_set_webhook_api_failure(self, mock_client_cls, mock_get_token):
        """Should return False when Telegram API returns error."""
        from api.services.telegram_service import TelegramService

        mock_get_token.return_value = "test-token"
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.post.return_value = mock_response
        mock_client_cls.return_value = mock_client

        result = TelegramService.set_webhook("https://example.com/webhook")
        assert result is False


class TestDeleteWebhook:
    """Tests for TelegramService.delete_webhook."""

    @patch("api.services.telegram_service.TelegramService._get_bot_token")
    @patch("api.services.telegram_service.httpx.Client")
    def test_delete_webhook_success(self, mock_client_cls, mock_get_token):
        """Should return True on successful webhook deletion."""
        from api.services.telegram_service import TelegramService

        mock_get_token.return_value = "test-token"
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.post.return_value = mock_response
        mock_client_cls.return_value = mock_client

        result = TelegramService.delete_webhook()
        assert result is True

    @patch("api.services.telegram_service.TelegramService._get_bot_token")
    def test_delete_webhook_no_token(self, mock_get_token):
        """Should return False when bot token is not set."""
        from api.services.telegram_service import TelegramService

        mock_get_token.return_value = None
        result = TelegramService.delete_webhook()
        assert result is False
