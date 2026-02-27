from __future__ import annotations

from datetime import datetime, timezone
import uuid

from sqlalchemy import Column, Index, String, Text, Integer, DateTime
from api.database.connection import Base


class Course(Base):
    __tablename__ = "courses"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    provider = Column(String(100), nullable=False)  # "Coursera", "Udemy"
    url = Column(String(500), nullable=False)
    instructor = Column(String(255), nullable=True)
    level = Column(String(50), nullable=False)  # beginner, intermediate, advanced
    duration = Column(String(100), nullable=True)  # e.g. "4 settimane", "20 ore"
    price = Column(String(100), nullable=True)  # e.g. "Gratis", "€49.99"
    rating = Column(String(10), nullable=True)  # e.g. "4.8"
    students_count = Column(Integer, nullable=True)
    category = Column(String(50), nullable=False)  # AI, ML, frontend, backend, devops
    tags_json = Column(Text, default="[]")  # JSON array stored as TEXT
    image_url = Column(String(500), nullable=True)
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index("ix_courses_is_active_created_at", "is_active", "created_at"),
        Index("ix_courses_category", "category"),
        Index("ix_courses_level", "level"),
    )
