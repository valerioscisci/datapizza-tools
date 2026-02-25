"""Pydantic schemas for notification endpoints."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


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

    class Config:
        from_attributes = True


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

    class Config:
        from_attributes = True


class NotificationPreferenceUpdate(BaseModel):
    email_notifications: Optional[bool] = None
    daily_digest: Optional[bool] = None
    channel: Optional[str] = None


class OkResponse(BaseModel):
    ok: bool


class MarkAllReadResponse(BaseModel):
    ok: bool
    count: int


class UnreadCountResponse(BaseModel):
    count: int


class DigestDisabledResponse(BaseModel):
    message: str
