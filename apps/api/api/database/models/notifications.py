from __future__ import annotations

from datetime import datetime, timezone
import uuid

from sqlalchemy import Column, Index, String, Text, Integer, DateTime, ForeignKey
from api.database.connection import Base


class EmailLog(Base):
    __tablename__ = "email_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    recipient_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    recipient_email = Column(String(255), nullable=False)
    sender_label = Column(String(255), default="Datapizza")
    email_type = Column(String(50), nullable=False)  # proposal_received, proposal_accepted, proposal_rejected, course_started, course_completed, milestone_reached, hiring_confirmation, daily_digest
    subject = Column(String(500), nullable=False)
    body_html = Column(Text, nullable=False)
    body_text = Column(Text, nullable=True)
    related_proposal_id = Column(String(36), ForeignKey("proposals.id"), nullable=True)
    is_read = Column(Integer, default=0)  # SQLite boolean
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index("ix_email_logs_recipient_id", "recipient_id"),
        Index("ix_email_logs_recipient_created", "recipient_id", "created_at"),
        Index("ix_email_logs_recipient_type", "recipient_id", "email_type"),
    )


class NotificationPreference(Base):
    __tablename__ = "notification_preferences"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), unique=True, nullable=False)
    email_notifications = Column(Integer, default=1)  # SQLite boolean
    daily_digest = Column(Integer, default=1)  # SQLite boolean
    channel = Column(String(50), default="email")  # "email", "telegram", "both"
    telegram_chat_id = Column(String(50), nullable=True)
    telegram_notifications = Column(Integer, default=0)  # SQLite boolean
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
