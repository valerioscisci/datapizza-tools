from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class EducationCreate(BaseModel):
    institution: str = Field(..., min_length=1, max_length=255, description="School or university name")
    degree: Optional[str] = Field(None, max_length=255, description="Degree name (e.g. Computer Science)")
    degree_type: Optional[str] = Field(None, max_length=50, description="e.g. Bachelor, Master, PhD")
    field_of_study: Optional[str] = Field(None, max_length=255, description="Field of study")
    start_year: int = Field(..., ge=1950, le=2030, description="Start year")
    end_year: Optional[int] = Field(None, ge=1950, le=2030, description="End year, ignored if is_current")
    is_current: bool = Field(False, description="Whether currently studying here")
    description: Optional[str] = Field(None, description="Additional details")


class EducationUpdate(BaseModel):
    institution: Optional[str] = Field(None, min_length=1, max_length=255, description="School or university name")
    degree: Optional[str] = Field(None, max_length=255, description="Degree name")
    degree_type: Optional[str] = Field(None, max_length=50, description="e.g. Bachelor, Master, PhD")
    field_of_study: Optional[str] = Field(None, max_length=255, description="Field of study")
    start_year: Optional[int] = Field(None, ge=1950, le=2030, description="Start year")
    end_year: Optional[int] = Field(None, ge=1950, le=2030, description="End year")
    is_current: Optional[bool] = Field(None, description="Whether currently studying here")
    description: Optional[str] = Field(None, description="Additional details")


class EducationResponse(BaseModel):
    id: str = Field(..., description="Unique education entry identifier")
    institution: str = Field(..., description="School or university name")
    degree: Optional[str] = Field(None, description="Degree name")
    degree_type: Optional[str] = Field(None, description="Degree type")
    field_of_study: Optional[str] = Field(None, description="Field of study")
    start_year: int = Field(..., description="Start year")
    end_year: Optional[int] = None
    is_current: bool = Field(..., description="Whether currently studying here")
    description: Optional[str] = None
    created_at: datetime = Field(..., description="Record creation timestamp")
