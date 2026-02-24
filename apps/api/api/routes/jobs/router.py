from __future__ import annotations

from typing import Literal, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from api.database.connection import get_db
from api.database.models import Job
from api.routes.jobs.schemas import JobResponse, JobListResponse
from api.utils import safe_parse_json_list

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.get("", response_model=JobListResponse)
async def list_jobs(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    work_mode: Optional[Literal["remote", "hybrid", "onsite"]] = None,
    db: Session = Depends(get_db),
):
    """List all active job listings with pagination."""
    query = db.query(Job).filter(Job.is_active == 1)

    if work_mode:
        query = query.filter(Job.work_mode == work_mode)

    total = query.count()
    jobs = query.order_by(Job.created_at.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()

    items = []
    for job in jobs:
        job_dict = {
            "id": job.id,
            "title": job.title,
            "company": job.company,
            "company_logo_url": job.company_logo_url,
            "location": job.location,
            "work_mode": job.work_mode,
            "description": job.description,
            "salary_min": job.salary_min,
            "salary_max": job.salary_max,
            "tags": safe_parse_json_list(job.tags_json),
            "experience_level": job.experience_level,
            "experience_years": job.experience_years,
            "employment_type": job.employment_type,
            "smart_working": job.smart_working,
            "welfare": job.welfare,
            "language": job.language,
            "apply_url": job.apply_url,
            "created_at": job.created_at,
            "updated_at": job.updated_at,
        }
        items.append(JobResponse(**job_dict))

    return JobListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )
