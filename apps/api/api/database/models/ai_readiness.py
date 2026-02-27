from __future__ import annotations

from datetime import datetime, timezone
import uuid

from sqlalchemy import Column, Index, String, Text, Integer, DateTime, ForeignKey
from api.database.connection import Base


class AIReadinessAssessment(Base):
    __tablename__ = "ai_readiness_assessments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    answers_json = Column(Text, nullable=False)  # JSON: {"q1_ai_coding_assistants": 3, ...}
    total_score = Column(Integer, nullable=False)  # 0-100 percentage
    readiness_level = Column(String(20), nullable=False)  # beginner/intermediate/advanced/expert
    quiz_version = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index("ix_ai_readiness_user_id", "user_id"),
        Index("ix_ai_readiness_user_created", "user_id", "created_at"),
    )
