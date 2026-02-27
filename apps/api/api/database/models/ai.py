from __future__ import annotations

from datetime import datetime, timezone
import uuid

from sqlalchemy import Column, Index, String, Text, DateTime, ForeignKey
from api.database.connection import Base


class AICache(Base):
    __tablename__ = "ai_cache"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    cache_type = Column(String(50), nullable=False)  # "job_matches" | "career_advice"
    content_json = Column(Text, nullable=False)  # Gemini JSON response
    model_used = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime, nullable=False)

    __table_args__ = (
        Index("ix_ai_cache_user_id_cache_type", "user_id", "cache_type"),
    )
