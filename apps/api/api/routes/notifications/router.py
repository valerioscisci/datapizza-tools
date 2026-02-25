"""Notification route handlers.

Endpoints for viewing emails, managing read status, preferences, and daily digest.
All endpoints require JWT auth via get_current_user.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional, Union

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from api.auth import get_current_user
from api.database.connection import get_db
from api.database.models import EmailLog, NotificationPreference, User
from api.routes.notifications.schemas import (
    DigestDisabledResponse,
    EmailLogListResponse,
    EmailLogResponse,
    MarkAllReadResponse,
    NotificationPreferenceResponse,
    NotificationPreferenceUpdate,
    OkResponse,
    UnreadCountResponse,
)
from api.services.email_service import EmailService

logger = structlog.get_logger()

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("/emails", response_model=EmailLogListResponse)
async def list_emails(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    email_type: Optional[list[str]] = Query(None),
    is_read: Optional[bool] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List the current user's emails with pagination and optional filtering."""
    query = db.query(EmailLog).filter(EmailLog.recipient_id == current_user.id)

    if email_type:
        query = query.filter(EmailLog.email_type.in_(email_type))

    if is_read is not None:
        query = query.filter(EmailLog.is_read == (1 if is_read else 0))

    total = query.count()

    unread_count = db.query(EmailLog).filter(
        EmailLog.recipient_id == current_user.id,
        EmailLog.is_read == 0,
    ).count()

    items = query.order_by(EmailLog.created_at.desc()).offset(
        (page - 1) * page_size,
    ).limit(page_size).all()

    return EmailLogListResponse(
        items=[
            EmailLogResponse(
                id=e.id,
                recipient_email=e.recipient_email,
                sender_label=e.sender_label or "Datapizza",
                email_type=e.email_type,
                subject=e.subject,
                body_html=e.body_html,
                body_text=e.body_text,
                related_proposal_id=e.related_proposal_id,
                is_read=bool(e.is_read),
                created_at=e.created_at,
            )
            for e in items
        ],
        total=total,
        page=page,
        page_size=page_size,
        unread_count=unread_count,
    )


@router.get("/emails/{email_id}", response_model=EmailLogResponse)
async def get_email(
    email_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a single email by ID. Auto-marks as read."""
    email = db.query(EmailLog).filter(
        EmailLog.id == email_id,
        EmailLog.recipient_id == current_user.id,
    ).first()

    if not email:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email not found",
        )

    # Auto-mark as read
    if not email.is_read:
        email.is_read = 1
        db.commit()
        db.refresh(email)

    return EmailLogResponse(
        id=email.id,
        recipient_email=email.recipient_email,
        sender_label=email.sender_label or "Datapizza",
        email_type=email.email_type,
        subject=email.subject,
        body_html=email.body_html,
        body_text=email.body_text,
        related_proposal_id=email.related_proposal_id,
        is_read=bool(email.is_read),
        created_at=email.created_at,
    )


@router.patch("/emails/{email_id}/read", response_model=OkResponse)
async def mark_email_read(
    email_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Mark a single email as read."""
    email = db.query(EmailLog).filter(
        EmailLog.id == email_id,
        EmailLog.recipient_id == current_user.id,
    ).first()

    if not email:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email not found",
        )

    email.is_read = 1
    db.commit()

    return {"ok": True}


@router.patch("/emails/read-all", response_model=MarkAllReadResponse)
async def mark_all_emails_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Mark all of the current user's unread emails as read."""
    count = db.query(EmailLog).filter(
        EmailLog.recipient_id == current_user.id,
        EmailLog.is_read == 0,
    ).update({"is_read": 1})
    db.commit()

    return {"ok": True, "count": count}


@router.get("/unread-count", response_model=UnreadCountResponse)
async def get_unread_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get the count of unread emails for the current user."""
    count = db.query(EmailLog).filter(
        EmailLog.recipient_id == current_user.id,
        EmailLog.is_read == 0,
    ).count()

    return {"count": count}


@router.get("/preferences", response_model=NotificationPreferenceResponse)
async def get_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get notification preferences. Returns defaults if no record exists."""
    pref = db.query(NotificationPreference).filter(
        NotificationPreference.user_id == current_user.id,
    ).first()

    if not pref:
        return NotificationPreferenceResponse(
            email_notifications=True,
            daily_digest=True,
            channel="email",
        )

    return NotificationPreferenceResponse(
        email_notifications=bool(pref.email_notifications),
        daily_digest=bool(pref.daily_digest),
        channel=pref.channel or "email",
    )


@router.patch("/preferences", response_model=NotificationPreferenceResponse)
async def update_preferences(
    data: NotificationPreferenceUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update notification preferences. Creates record if doesn't exist."""
    pref = db.query(NotificationPreference).filter(
        NotificationPreference.user_id == current_user.id,
    ).first()

    if not pref:
        pref = NotificationPreference(
            id=str(uuid.uuid4()),
            user_id=current_user.id,
            email_notifications=1,
            daily_digest=1,
            channel="email",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        db.add(pref)

    if data.email_notifications is not None:
        pref.email_notifications = 1 if data.email_notifications else 0
    if data.daily_digest is not None:
        pref.daily_digest = 1 if data.daily_digest else 0
    if data.channel is not None:
        pref.channel = data.channel

    pref.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(pref)

    return NotificationPreferenceResponse(
        email_notifications=bool(pref.email_notifications),
        daily_digest=bool(pref.daily_digest),
        channel=pref.channel or "email",
    )


@router.post("/daily-digest", response_model=Union[EmailLogResponse, DigestDisabledResponse])
async def trigger_daily_digest(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Trigger daily digest generation for the current user."""
    result = EmailService.generate_daily_digest(db, current_user)

    if result is None:
        return {"message": "Daily digest disabled"}

    return EmailLogResponse(
        id=result.id,
        recipient_email=result.recipient_email,
        sender_label=result.sender_label or "Datapizza",
        email_type=result.email_type,
        subject=result.subject,
        body_html=result.body_html,
        body_text=result.body_text,
        related_proposal_id=result.related_proposal_id,
        is_read=bool(result.is_read),
        created_at=result.created_at,
    )
