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


class Proposal(Base):
    __tablename__ = "proposals"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    talent_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    status = Column(String(50), nullable=False, default="sent")  # draft/sent/accepted/rejected/completed/hired
    message = Column(Text, nullable=True)
    budget_range = Column(String(100), nullable=True)
    total_xp = Column(Integer, default=0)
    hired_at = Column(DateTime, nullable=True)
    hiring_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index("ix_proposals_company_id", "company_id"),
        Index("ix_proposals_talent_id", "talent_id"),
        Index("ix_proposals_status", "status"),
    )


class ProposalCourse(Base):
    __tablename__ = "proposal_courses"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    proposal_id = Column(String(36), ForeignKey("proposals.id"), nullable=False)
    course_id = Column(String(36), ForeignKey("courses.id"), nullable=False)
    order = Column(Integer, nullable=False, default=0)
    is_completed = Column(Integer, default=0)
    completed_at = Column(DateTime, nullable=True)
    started_at = Column(DateTime, nullable=True)
    talent_notes = Column(Text, nullable=True)
    company_notes = Column(Text, nullable=True)
    deadline = Column(DateTime, nullable=True)
    xp_earned = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        UniqueConstraint("proposal_id", "course_id", name="uq_proposal_course"),
        Index("ix_proposal_courses_proposal_id", "proposal_id"),
    )


class ProposalMilestone(Base):
    __tablename__ = "proposal_milestones"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    proposal_id = Column(String(36), ForeignKey("proposals.id"), nullable=False)
    milestone_type = Column(String(50), nullable=False)  # course_started, course_completed, 25_percent, 50_percent, 75_percent, all_complete, streak_3, first_course
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    xp_reward = Column(Integer, default=0)
    achieved_at = Column(DateTime, nullable=False)

    __table_args__ = (
        Index("ix_proposal_milestones_proposal_id", "proposal_id"),
    )


class ProposalMessage(Base):
    __tablename__ = "proposal_messages"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    proposal_id = Column(String(36), ForeignKey("proposals.id"), nullable=False)
    sender_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index("ix_proposal_messages_proposal_id", "proposal_id"),
        Index("ix_proposal_messages_created_at", "created_at"),
    )


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
