from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ExperienceCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="Job title")
    company: str = Field(..., min_length=1, max_length=255, description="Company name")
    employment_type: Optional[str] = Field(None, max_length=50, description="e.g. full-time, part-time, freelance")
    location: Optional[str] = Field(None, max_length=255, description="Work location")
    start_month: Optional[int] = Field(None, ge=1, le=12, description="Start month (1-12)")
    start_year: int = Field(..., ge=1950, le=2030, description="Start year")
    end_month: Optional[int] = Field(None, ge=1, le=12, description="End month (1-12), ignored if is_current")
    end_year: Optional[int] = Field(None, ge=1950, le=2030, description="End year, ignored if is_current")
    is_current: bool = Field(False, description="Whether this is the current position")
    description: Optional[str] = Field(None, description="Role description")


class ExperienceUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255, description="Job title")
    company: Optional[str] = Field(None, min_length=1, max_length=255, description="Company name")
    employment_type: Optional[str] = Field(None, max_length=50, description="e.g. full-time, part-time, freelance")
    location: Optional[str] = Field(None, max_length=255, description="Work location")
    start_month: Optional[int] = Field(None, ge=1, le=12, description="Start month (1-12)")
    start_year: Optional[int] = Field(None, ge=1950, le=2030, description="Start year")
    end_month: Optional[int] = Field(None, ge=1, le=12, description="End month (1-12)")
    end_year: Optional[int] = Field(None, ge=1950, le=2030, description="End year")
    is_current: Optional[bool] = Field(None, description="Whether this is the current position")
    description: Optional[str] = Field(None, description="Role description")


class ExperienceResponse(BaseModel):
    id: str = Field(..., description="Unique experience identifier")
    title: str = Field(..., description="Job title")
    company: str = Field(..., description="Company name")
    employment_type: Optional[str] = Field(None, description="Employment type")
    location: Optional[str] = None
    start_month: Optional[int] = None
    start_year: int = Field(..., description="Start year")
    end_month: Optional[int] = None
    end_year: Optional[int] = None
    is_current: bool = Field(..., description="Whether this is the current position")
    description: Optional[str] = None
    created_at: datetime = Field(..., description="Record creation timestamp")
