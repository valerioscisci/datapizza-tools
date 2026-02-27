"""Notification route handlers.

Endpoints for viewing emails, managing read status, preferences, daily digest,
and Telegram webhook.
"""

from __future__ import annotations

import hmac
import os
import uuid
from datetime import datetime, timezone
from typing import Optional, Union

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from api.auth import get_current_user
from api.database.connection import get_db
from api.database.models import EmailLog, NotificationPreference, User
from api.routes.notifications.schemas import (
    BulkDigestResponse,
    DigestDisabledResponse,
    EMAIL_TYPE_VALUES,
    EmailLogListResponse,
    EmailLogResponse,
    MarkAllReadResponse,
    NotificationPreferenceResponse,
    NotificationPreferenceUpdate,
    OkResponse,
    TelegramLinkRequest,
    TelegramUpdate,
    UnreadCountResponse,
)
from api.services.email_service import EmailService
from api.services.telegram_service import TelegramService

logger = structlog.get_logger()

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("/emails", response_model=EmailLogListResponse)
async def list_emails(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    email_type: Optional[list[EMAIL_TYPE_VALUES]] = Query(None),
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


def _pref_to_response(pref: NotificationPreference) -> NotificationPreferenceResponse:
    """Convert a NotificationPreference model to a response schema."""
    return NotificationPreferenceResponse(
        email_notifications=bool(pref.email_notifications),
        daily_digest=bool(pref.daily_digest),
        channel=pref.channel or "email",
        telegram_chat_id=pref.telegram_chat_id,
        telegram_notifications=bool(pref.telegram_notifications),
    )


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
            telegram_chat_id=None,
            telegram_notifications=False,
        )

    return _pref_to_response(pref)


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
            telegram_chat_id=None,
            telegram_notifications=0,
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
    if data.telegram_notifications is not None:
        pref.telegram_notifications = 1 if data.telegram_notifications else 0

    pref.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(pref)

    return _pref_to_response(pref)


@router.post("/telegram/link", response_model=NotificationPreferenceResponse)
async def link_telegram(
    data: TelegramLinkRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Link a Telegram chat to the user's notification preferences.

    Saves the chat_id and enables telegram_notifications.
    """
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
            telegram_chat_id=data.chat_id,
            telegram_notifications=1,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        db.add(pref)
    else:
        pref.telegram_chat_id = data.chat_id
        pref.telegram_notifications = 1
        pref.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(pref)

    logger.info("telegram_linked", user_id=current_user.id, chat_id=data.chat_id)

    return _pref_to_response(pref)


@router.delete("/telegram/link", response_model=NotificationPreferenceResponse)
async def unlink_telegram(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Unlink Telegram from the user's notification preferences.

    Removes chat_id and disables telegram_notifications.
    """
    pref = db.query(NotificationPreference).filter(
        NotificationPreference.user_id == current_user.id,
    ).first()

    if not pref:
        return NotificationPreferenceResponse(
            email_notifications=True,
            daily_digest=True,
            channel="email",
            telegram_chat_id=None,
            telegram_notifications=False,
        )

    pref.telegram_chat_id = None
    pref.telegram_notifications = 0
    pref.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(pref)

    logger.info("telegram_unlinked", user_id=current_user.id)

    return _pref_to_response(pref)


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


@router.post(
    "/daily-digest/bulk",
    response_model=BulkDigestResponse,
    openapi_extra={"security": []},
    summary="Send daily digest to all opted-in users (cron/admin)",
    description=(
        "Iterates all users with daily_digest=True in NotificationPreference "
        "and generates a digest for each. Authenticated via X-API-Key header, "
        "not JWT. Intended for GitHub Action cron trigger."
    ),
)
async def trigger_bulk_daily_digest(
    request: Request,
    db: Session = Depends(get_db),
):
    """Send daily digest to ALL users who have daily_digest enabled."""
    # Validate API key
    api_key = os.getenv("CRON_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Bulk digest not configured",
        )

    provided_key = request.headers.get("X-API-Key", "")
    if not hmac.compare_digest(provided_key, api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )

    # Find all users with daily_digest enabled
    prefs = (
        db.query(NotificationPreference)
        .filter(NotificationPreference.daily_digest == 1)
        .all()
    )

    users_with_prefs = {p.user_id for p in prefs}
    all_active_users = db.query(User).filter(User.is_active == 1).all()

    # Users with explicit daily_digest=True
    target_users_from_prefs = [u for u in all_active_users if u.id in users_with_prefs]
    # Users with no preference record (default daily_digest=True)
    users_without_prefs = [u for u in all_active_users if u.id not in users_with_prefs]
    target_users = target_users_from_prefs + users_without_prefs

    sent = 0
    failed = 0
    skipped = 0
    errors: list[dict] = []

    for user in target_users:
        try:
            result = EmailService.generate_daily_digest(db, user)
            if result:
                sent += 1
            else:
                skipped += 1
        except Exception as e:
            failed += 1
            errors.append({"user_id": user.id, "error": str(e)})
            logger.error("bulk_digest_user_failed", user_id=user.id, error=str(e))

    logger.info(
        "bulk_digest_completed",
        sent=sent,
        skipped=skipped,
        failed=failed,
        total=len(target_users),
    )

    return BulkDigestResponse(
        sent=sent,
        skipped=skipped,
        failed=failed,
        total=len(target_users),
        errors=errors[:10],
    )


@router.post(
    "/telegram/webhook",
    response_model=OkResponse,
    openapi_extra={"security": []},
    summary="Telegram Bot webhook receiver",
    description=(
        "Receives updates from the Telegram Bot API. Public endpoint, no auth required. "
        "When a user sends /start, the bot replies with their Chat ID."
    ),
)
async def telegram_webhook(update: TelegramUpdate, request: Request):
    """Handle incoming Telegram webhook updates."""
    # Validate secret token if configured
    expected_secret = os.getenv("TELEGRAM_WEBHOOK_SECRET")
    if expected_secret:
        received_secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token", "")
        if received_secret != expected_secret:
            logger.warning("telegram_webhook_invalid_secret")
            return {"ok": True}

    if not update.message or not update.message.text:
        return {"ok": True}

    chat_id = str(update.message.chat.id)
    text = update.message.text.strip()

    logger.info("telegram_webhook_received", chat_id=chat_id, text=text)

    # Match /start or /start@botname
    if text == "/start" or text.startswith("/start@"):
        reply = (
            "<b>Ciao! Benvenuto su Datapizza Notify Bot.</b>\n\n"
            f"Il tuo Chat ID e': <code>{chat_id}</code>\n\n"
            "Copia questo ID e incollalo nella sezione "
            '"Collega Telegram" su Datapizza per attivare '
            "le notifiche Telegram."
        )
        sent = TelegramService.send_message(chat_id, reply)
        logger.info("telegram_webhook_start_reply", chat_id=chat_id, sent=sent)

    return {"ok": True}
