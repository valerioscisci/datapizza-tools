from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class EducationCreate(BaseModel):
    institution: str = Field(..., min_length=1, max_length=255)
    degree: Optional[str] = Field(None, max_length=255)
    degree_type: Optional[str] = Field(None, max_length=50)
    field_of_study: Optional[str] = Field(None, max_length=255)
    start_year: int = Field(..., ge=1950, le=2030)
    end_year: Optional[int] = Field(None, ge=1950, le=2030)
    is_current: bool = False
    description: Optional[str] = None


class EducationUpdate(BaseModel):
    institution: Optional[str] = Field(None, min_length=1, max_length=255)
    degree: Optional[str] = Field(None, max_length=255)
    degree_type: Optional[str] = Field(None, max_length=50)
    field_of_study: Optional[str] = Field(None, max_length=255)
    start_year: Optional[int] = Field(None, ge=1950, le=2030)
    end_year: Optional[int] = Field(None, ge=1950, le=2030)
    is_current: Optional[bool] = None
    description: Optional[str] = None


class EducationResponse(BaseModel):
    id: str
    institution: str
    degree: Optional[str] = None
    degree_type: Optional[str] = None
    field_of_study: Optional[str] = None
    start_year: int
    end_year: Optional[int] = None
    is_current: bool
    description: Optional[str] = None
    created_at: datetime
