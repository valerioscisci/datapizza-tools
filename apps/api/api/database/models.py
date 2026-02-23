from __future__ import annotations

from sqlalchemy import Column, Index, String, Text, Integer, DateTime, ForeignKey, UniqueConstraint
from api.database.connection import Base
from datetime import datetime, timezone
import uuid


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
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


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


class Job(Base):
    __tablename__ = "jobs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False)
    company = Column(String(255), nullable=False)
    company_logo_url = Column(String(500), nullable=True)
    location = Column(String(255), nullable=False)
    work_mode = Column(String(50), nullable=False)  # remote, hybrid, onsite
    description = Column(Text, nullable=False)
    salary_min = Column(Integer, nullable=True)
    salary_max = Column(Integer, nullable=True)
    tags_json = Column(Text, default="[]")  # JSON array stored as TEXT
    experience_level = Column(String(50), nullable=False)  # junior, mid, senior
    experience_years = Column(String(50), nullable=True)  # e.g. "3-4 anni", "4+ anni"
    employment_type = Column(String(50), default="full-time")  # full-time, part-time, contract
    smart_working = Column(String(100), nullable=True)  # e.g. "2-3 giorni/settimana", "1 giorno al mese in ufficio"
    welfare = Column(String(255), nullable=True)  # e.g. "Welfare aziendale di € 1.000"
    language = Column(String(100), nullable=True)  # e.g. "Inglese: B2"
    apply_url = Column(String(500), nullable=True)
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
