from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

from api.schemas.experience import ExperienceResponse
from api.schemas.education import EducationResponse


class TalentCardResponse(BaseModel):
    """Public-safe summary for talent list. NEVER includes email, phone, password_hash."""

    id: str
    full_name: str
    current_role: Optional[str] = None
    location: Optional[str] = None
    skills: list[str] = Field(default_factory=list)
    experience_level: Optional[str] = None
    experience_years: Optional[str] = None
    availability_status: str = "available"
    bio: Optional[str] = None


class TalentCardListResponse(BaseModel):
    items: list[TalentCardResponse]
    total: int
    page: int
    page_size: int


class TalentDetailResponse(BaseModel):
    """Full public profile. NEVER includes email, phone, password_hash, reskilling_status, adopted_by_company."""

    id: str
    full_name: str
    bio: Optional[str] = None
    current_role: Optional[str] = None
    location: Optional[str] = None
    experience_level: Optional[str] = None
    experience_years: Optional[str] = None
    skills: list[str] = Field(default_factory=list)
    availability_status: str = "available"
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    experiences: list[ExperienceResponse] = Field(default_factory=list)
    educations: list[EducationResponse] = Field(default_factory=list)
    created_at: datetime
