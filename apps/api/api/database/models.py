from __future__ import annotations

from sqlalchemy import Column, String, Text, Integer, DateTime
from api.database.connection import Base
from datetime import datetime, timezone
import uuid


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
