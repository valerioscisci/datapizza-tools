from __future__ import annotations

from datetime import datetime, timezone
import uuid

from sqlalchemy import Column, Index, String, Text, Integer, DateTime
from api.database.connection import Base


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=True)
    bio = Column(Text, nullable=True)
    location = Column(String(255), nullable=True)
    experience_level = Column(String(50), nullable=True)  # junior/mid/senior
    experience_years = Column(String(50), nullable=True)  # e.g. "3-4 anni"
    current_role = Column(String(255), nullable=True)  # e.g. "Frontend Developer"
    skills_json = Column(Text, default="[]")  # JSON array stored as TEXT
    availability_status = Column(String(50), default="available")  # available/employed/reskilling
    reskilling_status = Column(String(50), nullable=True)  # null/in_progress/completed
    adopted_by_company = Column(String(255), nullable=True)  # company name, for CYD flow
    linkedin_url = Column(String(500), nullable=True)
    github_url = Column(String(500), nullable=True)
    portfolio_url = Column(String(500), nullable=True)
    user_type = Column(String(50), nullable=False, default="talent")  # "talent" or "company"
    company_name = Column(String(255), nullable=True)
    company_website = Column(String(500), nullable=True)
    company_size = Column(String(100), nullable=True)  # "1-10", "11-50", "51-200", "201-500", "500+"
    industry = Column(String(255), nullable=True)
    is_public = Column(Integer, default=0)
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index("ix_users_is_public_is_active", "is_public", "is_active"),
        Index("ix_users_user_type", "user_type"),
    )
