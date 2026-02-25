from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class JobResponse(BaseModel):
    id: str = Field(..., description="Unique job listing identifier")
    title: str = Field(..., description="Job title")
    company: str = Field(..., description="Company name")
    company_logo_url: Optional[str] = Field(None, description="URL of the company logo")
    location: str = Field(..., description="Job location (city or region)")
    work_mode: str = Field(..., description="Work mode: remote, hybrid, or onsite")
    description: str = Field(..., description="Full job description")
    salary_min: Optional[int] = Field(None, description="Minimum salary (EUR)")
    salary_max: Optional[int] = Field(None, description="Maximum salary (EUR)")
    tags: list[str] = Field(default_factory=list, description="Technology/skill tags")
    experience_level: str = Field(..., description="Required experience level")
    experience_years: Optional[str] = None
    employment_type: str = Field(..., description="e.g. full-time, part-time, contract")
    smart_working: Optional[str] = None
    welfare: Optional[str] = None
    language: Optional[str] = Field(None, description="Required language")
    apply_url: Optional[str] = Field(None, description="External application URL")
    created_at: datetime = Field(..., description="Job listing creation timestamp")
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class JobListResponse(BaseModel):
    items: list[JobResponse] = Field(..., description="List of job listings")
    total: int = Field(..., description="Total number of matching jobs")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
