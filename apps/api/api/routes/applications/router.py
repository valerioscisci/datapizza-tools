from __future__ import annotations

from typing import Literal, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from api.database.connection import get_db
from api.database.models import Application, Job, User
from api.routes.applications.schemas import ApplicationCreate, ApplicationResponse, ApplicationListResponse
from api.routes.jobs.schemas import JobResponse
from api.auth import get_current_user
from api.utils import safe_parse_json_list

router = APIRouter(prefix="/applications", tags=["Applications"])

STATUS_TABS = ["proposta", "da_completare", "attiva", "archiviata"]


def _build_application_response(app: Application, job: Job) -> ApplicationResponse:
    job_resp = JobResponse(
        id=job.id,
        title=job.title,
        company=job.company,
        company_logo_url=job.company_logo_url,
        location=job.location,
        work_mode=job.work_mode,
        description=job.description,
        salary_min=job.salary_min,
        salary_max=job.salary_max,
        tags=safe_parse_json_list(job.tags_json),
        experience_level=job.experience_level,
        experience_years=job.experience_years,
        employment_type=job.employment_type,
        smart_working=job.smart_working,
        welfare=job.welfare,
        language=job.language,
        apply_url=job.apply_url,
        created_at=job.created_at,
        updated_at=job.updated_at,
    )
    return ApplicationResponse(
        id=app.id,
        job=job_resp,
        status=app.status,
        status_detail=app.status_detail,
        recruiter_name=app.recruiter_name,
        recruiter_role=app.recruiter_role,
        applied_at=app.applied_at,
        updated_at=app.updated_at,
    )


@router.post(
    "",
    response_model=ApplicationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Apply to a job listing",
    responses={
        401: {"description": "Not authenticated"},
        404: {"description": "Job not found"},
        409: {"description": "Already applied to this job"},
    },
)
async def create_application(
    data: ApplicationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Submit an application to an active job listing. A user can only apply once per job."""
    job = db.query(Job).filter(Job.id == data.job_id, Job.is_active == 1).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    existing = db.query(Application).filter(
        Application.user_id == current_user.id,
        Application.job_id == data.job_id,
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Already applied to this job",
        )

    application = Application(
        user_id=current_user.id,
        job_id=data.job_id,
        status="attiva",
        status_detail="In valutazione",
    )
    db.add(application)
    db.commit()
    db.refresh(application)

    return _build_application_response(application, job)


@router.get(
    "",
    response_model=ApplicationListResponse,
    summary="List my job applications",
    responses={
        401: {"description": "Not authenticated"},
    },
)
async def list_applications(
    status_filter: Optional[Literal["proposta", "da_completare", "attiva", "archiviata"]] = Query(None, alias="status"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Count per status tab
    counts_query = db.query(
        Application.status, func.count(Application.id)
    ).filter(Application.user_id == current_user.id).group_by(Application.status).all()

    counts = {s: 0 for s in STATUS_TABS}
    for s, c in counts_query:
        counts[s] = c

    # Join applications with jobs in a single query (fixes N+1)
    query = db.query(Application, Job).join(
        Job, Application.job_id == Job.id
    ).filter(Application.user_id == current_user.id)

    if status_filter:
        query = query.filter(Application.status == status_filter)

    results = query.order_by(Application.applied_at.desc()).all()

    items = [_build_application_response(app, job) for app, job in results]

    return ApplicationListResponse(
        items=items,
        total=len(items),
        counts=counts,
    )


@router.get(
    "/{application_id}",
    response_model=ApplicationResponse,
    summary="Get application details",
    responses={
        401: {"description": "Not authenticated"},
        404: {"description": "Application not found"},
    },
)
async def get_application(
    application_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    result = db.query(Application, Job).join(
        Job, Application.job_id == Job.id
    ).filter(
        Application.id == application_id,
        Application.user_id == current_user.id,
    ).first()
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )
    app, job = result

    return _build_application_response(app, job)
