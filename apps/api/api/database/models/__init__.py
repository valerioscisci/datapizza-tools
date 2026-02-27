"""Database models package.

Re-exports all models for backward-compatible imports:
    from api.database.models import User, Job, ...
"""

from api.database.models.user import User
from api.database.models.profile import Experience, Education
from api.database.models.jobs import Job
from api.database.models.applications import Application
from api.database.models.proposals import (
    Proposal,
    ProposalCourse,
    ProposalMilestone,
    ProposalMessage,
)
from api.database.models.news import News
from api.database.models.courses import Course
from api.database.models.ai import AICache
from api.database.models.notifications import EmailLog, NotificationPreference
from api.database.models.ai_readiness import AIReadinessAssessment

__all__ = [
    "User",
    "Experience",
    "Education",
    "Job",
    "Application",
    "Proposal",
    "ProposalCourse",
    "ProposalMilestone",
    "ProposalMessage",
    "News",
    "Course",
    "AICache",
    "EmailLog",
    "NotificationPreference",
    "AIReadinessAssessment",
]
