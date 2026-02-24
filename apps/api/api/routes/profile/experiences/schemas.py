from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ExperienceCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    company: str = Field(..., min_length=1, max_length=255)
    employment_type: Optional[str] = Field(None, max_length=50)
    location: Optional[str] = Field(None, max_length=255)
    start_month: Optional[int] = Field(None, ge=1, le=12)
    start_year: int = Field(..., ge=1950, le=2030)
    end_month: Optional[int] = Field(None, ge=1, le=12)
    end_year: Optional[int] = Field(None, ge=1950, le=2030)
    is_current: bool = False
    description: Optional[str] = None


class ExperienceUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    company: Optional[str] = Field(None, min_length=1, max_length=255)
    employment_type: Optional[str] = Field(None, max_length=50)
    location: Optional[str] = Field(None, max_length=255)
    start_month: Optional[int] = Field(None, ge=1, le=12)
    start_year: Optional[int] = Field(None, ge=1950, le=2030)
    end_month: Optional[int] = Field(None, ge=1, le=12)
    end_year: Optional[int] = Field(None, ge=1950, le=2030)
    is_current: Optional[bool] = None
    description: Optional[str] = None


class ExperienceResponse(BaseModel):
    id: str
    title: str
    company: str
    employment_type: Optional[str] = None
    location: Optional[str] = None
    start_month: Optional[int] = None
    start_year: int
    end_month: Optional[int] = None
    end_year: Optional[int] = None
    is_current: bool
    description: Optional[str] = None
    created_at: datetime
