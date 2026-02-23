from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from api.schemas.job import JobResponse


class ApplicationCreate(BaseModel):
    job_id: str = Field(..., min_length=1)


class ApplicationResponse(BaseModel):
    id: str
    job: JobResponse
    status: str
    status_detail: Optional[str] = None
    recruiter_name: Optional[str] = None
    recruiter_role: Optional[str] = None
    applied_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ApplicationListResponse(BaseModel):
    items: list[ApplicationResponse]
    total: int
    counts: dict[str, int] = Field(default_factory=dict)
