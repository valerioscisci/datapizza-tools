"""Telegram Bot notification service.

Sends notifications to users who have linked their Telegram account.
Uses httpx to call the Telegram Bot API. Gracefully degrades if the
bot token is not configured or the user has not linked Telegram.
"""

from __future__ import annotations

import os

import httpx
import structlog
from sqlalchemy.orm import Session

from api.database.models import NotificationPreference

logger = structlog.get_logger()

TELEGRAM_API_BASE = "https://api.telegram.org"


class TelegramService:
    """Static service for sending Telegram notifications."""

    @staticmethod
    def _get_bot_token() -> str | None:
        """Read the bot token from the environment."""
        return os.getenv("TELEGRAM_BOT_TOKEN")

    @staticmethod
    def send_message(chat_id: str, text: str) -> bool:
        """Send a text message to a Telegram chat.

        Returns True on success, False on failure.
        """
        token = TelegramService._get_bot_token()
        if not token:
            logger.warning("telegram_bot_token_not_set")
            return False

        url = f"{TELEGRAM_API_BASE}/bot{token}/sendMessage"
        payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}

        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.post(url, json=payload)
                if response.status_code == 200:
                    logger.info("telegram_message_sent", chat_id=chat_id)
                    return True
                else:
                    logger.error(
                        "telegram_send_failed",
                        chat_id=chat_id,
                        status_code=response.status_code,
                        response_body=response.text[:200],
                    )
                    return False
        except Exception as e:
            logger.error("telegram_send_error", chat_id=chat_id, error=str(e))
            return False

    @staticmethod
    def send_notification(db: Session, recipient_id: str, text: str) -> bool:
        """Send a notification via Telegram if the user has it enabled.

        Checks the user's NotificationPreference for telegram_notifications
        being enabled AND telegram_chat_id being set.

        Returns True if sent, False otherwise (disabled, no chat_id, or error).
        """
        pref = db.query(NotificationPreference).filter(
            NotificationPreference.user_id == recipient_id,
        ).first()

        if not pref:
            return False

        if not pref.telegram_notifications:
            return False

        if not pref.telegram_chat_id:
            logger.info("telegram_chat_id_missing", user_id=recipient_id)
            return False

        return TelegramService.send_message(pref.telegram_chat_id, text)

    @staticmethod
    def set_webhook(webhook_url: str, secret_token: str | None = None) -> bool:
        """Register a webhook URL with the Telegram Bot API.

        Returns True on success, False on failure.
        """
        token = TelegramService._get_bot_token()
        if not token:
            logger.warning("telegram_bot_token_not_set")
            return False

        url = f"{TELEGRAM_API_BASE}/bot{token}/setWebhook"
        payload: dict = {"url": webhook_url, "allowed_updates": ["message"]}
        if secret_token:
            payload["secret_token"] = secret_token

        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.post(url, json=payload)
                if response.status_code == 200 and response.json().get("ok"):
                    logger.info("telegram_webhook_set", url=webhook_url)
                    return True
                logger.error(
                    "telegram_webhook_set_failed",
                    status_code=response.status_code,
                    body=response.text[:200],
                )
                return False
        except Exception as e:
            logger.error("telegram_webhook_set_error", error=str(e))
            return False

    @staticmethod
    def delete_webhook() -> bool:
        """Remove the webhook from the Telegram Bot API."""
        token = TelegramService._get_bot_token()
        if not token:
            return False

        url = f"{TELEGRAM_API_BASE}/bot{token}/deleteWebhook"
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.post(url)
                return response.status_code == 200
        except Exception:
            return False
