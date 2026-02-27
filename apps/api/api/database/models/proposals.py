from __future__ import annotations

from datetime import datetime, timezone
import uuid

from sqlalchemy import Column, Index, String, Text, Integer, DateTime, ForeignKey, UniqueConstraint
from api.database.connection import Base


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
