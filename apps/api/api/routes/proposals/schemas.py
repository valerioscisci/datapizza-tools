from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class MilestoneResponse(BaseModel):
    id: str
    milestone_type: str
    title: str
    description: Optional[str] = None
    xp_reward: int = 0
    achieved_at: datetime


class ProposalCourseResponse(BaseModel):
    id: str
    course_id: str
    course_title: str
    course_provider: str
    course_level: str
    course_url: Optional[str] = None
    course_duration: Optional[str] = None
    course_category: Optional[str] = None
    order: int
    is_completed: bool
    completed_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    talent_notes: Optional[str] = None
    company_notes: Optional[str] = None
    deadline: Optional[datetime] = None
    xp_earned: int = 0
    is_overdue: bool = False
    days_remaining: Optional[int] = None


class ProposalCreate(BaseModel):
    talent_id: str = Field(..., min_length=1)
    message: Optional[str] = None
    budget_range: Optional[str] = Field(None, max_length=100)
    course_ids: list[str] = Field(..., min_length=1)


class ProposalUpdate(BaseModel):
    status: Optional[str] = Field(None, pattern=r"^(draft|sent|accepted|rejected|completed|hired)$")
    message: Optional[str] = None
    budget_range: Optional[str] = Field(None, max_length=100)
    hiring_notes: Optional[str] = None


class ProposalResponse(BaseModel):
    id: str
    company_id: str
    company_name: str
    talent_id: str
    talent_name: str
    status: str
    message: Optional[str] = None
    budget_range: Optional[str] = None
    courses: list[ProposalCourseResponse] = Field(default_factory=list)
    progress: float = 0.0
    total_xp: int = 0
    milestones: list[MilestoneResponse] = Field(default_factory=list)
    hired_at: Optional[datetime] = None
    hiring_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class ProposalListResponse(BaseModel):
    items: list[ProposalResponse]
    total: int
    page: int
    page_size: int


class CourseNotesUpdate(BaseModel):
    talent_notes: Optional[str] = None


class CompanyCourseUpdate(BaseModel):
    company_notes: Optional[str] = None
    deadline: Optional[datetime] = None
