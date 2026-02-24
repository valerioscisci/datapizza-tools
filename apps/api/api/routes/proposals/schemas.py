from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ProposalCourseResponse(BaseModel):
    id: str
    course_id: str
    course_title: str
    course_provider: str
    course_level: str
    order: int
    is_completed: bool
    completed_at: Optional[datetime] = None


class ProposalCreate(BaseModel):
    talent_id: str = Field(..., min_length=1)
    message: Optional[str] = None
    budget_range: Optional[str] = Field(None, max_length=100)
    course_ids: list[str] = Field(..., min_length=1)


class ProposalUpdate(BaseModel):
    status: Optional[str] = Field(None, pattern=r"^(draft|sent|accepted|rejected|completed)$")
    message: Optional[str] = None
    budget_range: Optional[str] = Field(None, max_length=100)


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
    created_at: datetime
    updated_at: datetime


class ProposalListResponse(BaseModel):
    items: list[ProposalResponse]
    total: int
    page: int
    page_size: int
