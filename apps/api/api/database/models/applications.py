from __future__ import annotations

from datetime import datetime, timezone
import uuid

from sqlalchemy import Column, Index, String, Text, Integer, DateTime, ForeignKey, UniqueConstraint
from api.database.connection import Base


class Application(Base):
    __tablename__ = "applications"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    job_id = Column(String(36), ForeignKey("jobs.id"), nullable=False)
    status = Column(String(50), nullable=False, default="attiva")  # proposta/da_completare/attiva/archiviata
    status_detail = Column(String(255), nullable=True)  # e.g. "In valutazione", "Questionario da completare"
    recruiter_name = Column(String(255), nullable=True)
    recruiter_role = Column(String(255), nullable=True)
    applied_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        UniqueConstraint("user_id", "job_id", name="uq_user_job"),
        Index("ix_applications_user_id", "user_id"),
        Index("ix_applications_status", "status"),
    )
