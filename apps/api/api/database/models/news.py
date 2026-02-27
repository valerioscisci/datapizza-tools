from __future__ import annotations

from datetime import datetime, timezone
import uuid

from sqlalchemy import Column, Index, String, Text, Integer, DateTime
from api.database.connection import Base


class News(Base):
    __tablename__ = "news"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False)
    summary = Column(Text, nullable=False)
    source = Column(String(100), nullable=False)  # "Hacker News", "TLDR Tech"
    source_url = Column(String(500), nullable=True)
    category = Column(String(50), nullable=False)  # AI, tech, careers
    tags_json = Column(Text, default="[]")  # JSON array stored as TEXT
    author = Column(String(255), nullable=True)
    published_at = Column(DateTime, nullable=False)
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index("ix_news_is_active_published_at", "is_active", "published_at"),
        Index("ix_news_category", "category"),
    )
