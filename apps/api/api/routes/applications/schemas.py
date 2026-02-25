from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from api.routes.jobs.schemas import JobResponse


class ApplicationCreate(BaseModel):
    job_id: str = Field(..., min_length=1, description="ID of the job to apply to")


class ApplicationResponse(BaseModel):
    id: str = Field(..., description="Unique application identifier")
    job: JobResponse = Field(..., description="The job listing applied to")
    status: str = Field(..., description="Application status: proposta, da_completare, attiva, archiviata")
    status_detail: Optional[str] = Field(None, description="Human-readable status detail")
    recruiter_name: Optional[str] = None
    recruiter_role: Optional[str] = None
    applied_at: datetime = Field(..., description="When the application was submitted")
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ApplicationListResponse(BaseModel):
    items: list[ApplicationResponse] = Field(..., description="List of applications")
    total: int = Field(..., description="Total number of applications")
    counts: dict[str, int] = Field(default_factory=dict, description="Count of applications per status tab")
