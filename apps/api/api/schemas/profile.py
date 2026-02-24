from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

from api.schemas.experience import ExperienceResponse
from api.schemas.education import EducationResponse


class ProfileUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=1, max_length=255)
    phone: Optional[str] = Field(None, max_length=50)
    bio: Optional[str] = None
    location: Optional[str] = Field(None, max_length=255)
    experience_level: Optional[str] = Field(None, max_length=50)
    experience_years: Optional[str] = Field(None, max_length=50)
    current_role: Optional[str] = Field(None, max_length=255)
    skills: Optional[list[str]] = None
    availability_status: Optional[str] = Field(None, max_length=50)
    linkedin_url: Optional[str] = Field(None, max_length=500)
    github_url: Optional[str] = Field(None, max_length=500)
    portfolio_url: Optional[str] = Field(None, max_length=500)
    is_public: Optional[bool] = None
    company_name: Optional[str] = Field(None, min_length=1, max_length=255)
    company_website: Optional[str] = Field(None, max_length=500)
    company_size: Optional[str] = Field(None, max_length=100)
    industry: Optional[str] = Field(None, max_length=255)


class ProfileResponse(BaseModel):
    id: str
    email: str
    full_name: str
    phone: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    experience_level: Optional[str] = None
    experience_years: Optional[str] = None
    current_role: Optional[str] = None
    skills: list[str] = Field(default_factory=list)
    availability_status: str = "available"
    reskilling_status: Optional[str] = None
    adopted_by_company: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    user_type: str = "talent"
    company_name: Optional[str] = None
    company_website: Optional[str] = None
    company_size: Optional[str] = None
    industry: Optional[str] = None
    is_public: bool = False
    experiences: list[ExperienceResponse] = Field(default_factory=list)
    educations: list[EducationResponse] = Field(default_factory=list)
    created_at: datetime
