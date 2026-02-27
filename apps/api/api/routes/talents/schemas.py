from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

from api.routes.profile.experiences.schemas import ExperienceResponse
from api.routes.profile.educations.schemas import EducationResponse


class TalentCardResponse(BaseModel):
    """Public-safe summary for talent list. NEVER includes email, phone, password_hash."""

    id: str = Field(description="Unique talent identifier")
    full_name: str = Field(description="Talent's display name")
    current_role: Optional[str] = Field(None, description="Current job title or role")
    location: Optional[str] = Field(None, description="City or region")
    skills: list[str] = Field(default_factory=list, description="List of technical and soft skills")
    experience_level: Optional[str] = Field(None, description="Seniority level (junior, mid, senior)")
    experience_years: Optional[str] = Field(None, description="Years of professional experience")
    availability_status: str = Field("available", description="Current availability: available, open_to_offers, employed")
    bio: Optional[str] = Field(None, description="Short biography")
    ai_readiness_score: Optional[int] = Field(None, description="AI readiness score (0-100), null if never taken")
    ai_readiness_level: Optional[str] = Field(None, description="AI readiness level: beginner, intermediate, advanced, expert")


class TalentCardListResponse(BaseModel):
    items: list[TalentCardResponse] = Field(description="List of talent cards for the current page")
    total: int = Field(description="Total number of matching talents")
    page: int = Field(description="Current page number (1-based)")
    page_size: int = Field(description="Number of items per page")


class TalentDetailResponse(BaseModel):
    """Full public profile. NEVER includes email, phone, password_hash, reskilling_status, adopted_by_company."""

    id: str = Field(description="Unique talent identifier")
    full_name: str = Field(description="Talent's display name")
    bio: Optional[str] = Field(None, description="Short biography")
    current_role: Optional[str] = Field(None, description="Current job title or role")
    location: Optional[str] = Field(None, description="City or region")
    experience_level: Optional[str] = Field(None, description="Seniority level (junior, mid, senior)")
    experience_years: Optional[str] = Field(None, description="Years of professional experience")
    skills: list[str] = Field(default_factory=list, description="List of technical and soft skills")
    availability_status: str = Field("available", description="Current availability: available, open_to_offers, employed")
    linkedin_url: Optional[str] = Field(None, description="LinkedIn profile URL")
    github_url: Optional[str] = Field(None, description="GitHub profile URL")
    portfolio_url: Optional[str] = Field(None, description="Personal portfolio or website URL")
    ai_readiness_score: Optional[int] = Field(None, description="AI readiness score (0-100), null if never taken")
    ai_readiness_level: Optional[str] = Field(None, description="AI readiness level: beginner, intermediate, advanced, expert")
    experiences: list[ExperienceResponse] = Field(default_factory=list, description="Work experience entries")
    educations: list[EducationResponse] = Field(default_factory=list, description="Education entries")
    created_at: datetime = Field(description="When the talent profile was created")
