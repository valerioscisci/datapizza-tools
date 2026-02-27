from __future__ import annotations

from datetime import datetime, timezone
import uuid

from sqlalchemy import Column, Index, String, Text, Integer, DateTime, ForeignKey
from api.database.connection import Base


class Experience(Base):
    __tablename__ = "experiences"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)  # Job title
    company = Column(String(255), nullable=False)
    employment_type = Column(String(50), nullable=True)  # full-time, part-time, contract, freelance
    location = Column(String(255), nullable=True)
    start_month = Column(Integer, nullable=True)  # 1-12
    start_year = Column(Integer, nullable=False)
    end_month = Column(Integer, nullable=True)  # 1-12
    end_year = Column(Integer, nullable=True)  # null if is_current
    is_current = Column(Integer, default=0)  # SQLite boolean
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index("ix_experiences_user_id", "user_id"),
    )


class Education(Base):
    __tablename__ = "educations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    institution = Column(String(255), nullable=False)
    degree = Column(String(255), nullable=True)  # e.g. "Laurea Magistrale"
    degree_type = Column(String(50), nullable=True)  # bachelor, master, phd, diploma, certificate
    field_of_study = Column(String(255), nullable=True)  # e.g. "Informatica"
    start_year = Column(Integer, nullable=False)
    end_year = Column(Integer, nullable=True)  # null if is_current
    is_current = Column(Integer, default=0)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index("ix_educations_user_id", "user_id"),
    )
