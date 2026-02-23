from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class JobResponse(BaseModel):
    id: str
    title: str
    company: str
    company_logo_url: Optional[str] = None
    location: str
    work_mode: str
    description: str
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    tags: list[str] = Field(default_factory=list)
    experience_level: str
    experience_years: Optional[str] = None
    employment_type: str
    smart_working: Optional[str] = None
    welfare: Optional[str] = None
    language: Optional[str] = None
    apply_url: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class JobListResponse(BaseModel):
    items: list[JobResponse]
    total: int
    page: int
    page_size: int
