"""Pydantic schemas for notification endpoints."""

from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

# Valid email_type values
EMAIL_TYPE_VALUES = Literal[
    "proposal_received",
    "proposal_accepted",
    "proposal_rejected",
    "course_started",
    "course_completed",
    "milestone_reached",
    "hiring_confirmation",
    "daily_digest",
]

# Valid channel values
CHANNEL_VALUES = Literal["email", "telegram", "both"]


class EmailLogResponse(BaseModel):
    id: str
    recipient_email: str
    sender_label: str
    email_type: str
    subject: str
    body_html: str
    body_text: Optional[str] = None
    related_proposal_id: Optional[str] = None
    is_read: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EmailLogListResponse(BaseModel):
    items: list[EmailLogResponse]
    total: int
    page: int
    page_size: int
    unread_count: int


class NotificationPreferenceResponse(BaseModel):
    email_notifications: bool
    daily_digest: bool
    channel: str
    telegram_chat_id: Optional[str] = None
    telegram_notifications: bool = False

    model_config = ConfigDict(from_attributes=True)


class NotificationPreferenceUpdate(BaseModel):
    email_notifications: Optional[bool] = None
    daily_digest: Optional[bool] = None
    channel: Optional[CHANNEL_VALUES] = None
    telegram_notifications: Optional[bool] = None


class TelegramLinkRequest(BaseModel):
    chat_id: str = Field(..., min_length=1, max_length=50, pattern=r"^-?\d+$")


class OkResponse(BaseModel):
    ok: bool


class MarkAllReadResponse(BaseModel):
    ok: bool
    count: int


class UnreadCountResponse(BaseModel):
    count: int


class DigestDisabledResponse(BaseModel):
    message: str


# --- Telegram Webhook schemas ---


class TelegramChat(BaseModel):
    """Subset of Telegram Chat object."""

    id: int


class TelegramMessage(BaseModel):
    """Subset of Telegram Message object."""

    chat: TelegramChat
    text: Optional[str] = None


class TelegramUpdate(BaseModel):
    """Telegram Update received via webhook.

    Only ``message`` updates with text are relevant; other update types
    (edited_message, callback_query, etc.) are ignored.
    """

    update_id: int
    message: Optional[TelegramMessage] = None
