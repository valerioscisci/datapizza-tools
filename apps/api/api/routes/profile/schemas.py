from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

from api.routes.profile.experiences.schemas import ExperienceResponse
from api.routes.profile.educations.schemas import EducationResponse


class ProfileUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=1, max_length=255, description="User full name")
    phone: Optional[str] = Field(None, max_length=50, description="Phone number")
    bio: Optional[str] = Field(None, description="Short biography")
    location: Optional[str] = Field(None, max_length=255, description="City or region")
    experience_level: Optional[str] = Field(None, max_length=50, description="e.g. junior, mid, senior")
    experience_years: Optional[str] = Field(None, max_length=50, description="Years of experience")
    current_role: Optional[str] = Field(None, max_length=255, description="Current job title")
    skills: Optional[list[str]] = Field(None, description="List of skill tags")
    availability_status: Optional[str] = Field(None, max_length=50, description="Job availability status")
    linkedin_url: Optional[str] = Field(None, max_length=500, description="LinkedIn profile URL")
    github_url: Optional[str] = Field(None, max_length=500, description="GitHub profile URL")
    portfolio_url: Optional[str] = Field(None, max_length=500, description="Portfolio website URL")
    is_public: Optional[bool] = Field(None, description="Whether profile is visible to companies")
    company_name: Optional[str] = Field(None, min_length=1, max_length=255, description="Company name (company accounts)")
    company_website: Optional[str] = Field(None, max_length=500, description="Company website URL")
    company_size: Optional[str] = Field(None, max_length=100, description="Company size range")
    industry: Optional[str] = Field(None, max_length=255, description="Industry sector")


class ProfileResponse(BaseModel):
    id: str = Field(..., description="Unique user identifier")
    email: str = Field(..., description="User email address")
    full_name: str = Field(..., description="User full name")
    phone: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    experience_level: Optional[str] = Field(None, description="e.g. junior, mid, senior")
    experience_years: Optional[str] = None
    current_role: Optional[str] = None
    skills: list[str] = Field(default_factory=list, description="List of skill tags")
    availability_status: str = Field("available", description="Job availability status")
    reskilling_status: Optional[str] = None
    adopted_by_company: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    user_type: str = Field("talent", description="Account type: 'talent' or 'company'")
    company_name: Optional[str] = None
    company_website: Optional[str] = None
    company_size: Optional[str] = None
    industry: Optional[str] = None
    ai_readiness_score: Optional[int] = Field(None, description="AI readiness score (0-100), null if never taken")
    ai_readiness_level: Optional[str] = Field(None, description="AI readiness level: beginner, intermediate, advanced, expert")
    is_public: bool = Field(False, description="Whether profile is visible to companies")
    experiences: list[ExperienceResponse] = Field(default_factory=list, description="Work experiences")
    educations: list[EducationResponse] = Field(default_factory=list, description="Education entries")
    created_at: datetime = Field(..., description="Account creation timestamp")
