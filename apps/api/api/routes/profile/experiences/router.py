from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.database.connection import get_db
from api.database.models import User, Experience
from api.routes.profile.experiences.schemas import ExperienceCreate, ExperienceUpdate, ExperienceResponse
from api.auth import get_current_user

router = APIRouter(prefix="/experiences", tags=["Profile - Experiences"])


def _experience_to_response(exp: Experience) -> ExperienceResponse:
    return ExperienceResponse(
        id=exp.id,
        title=exp.title,
        company=exp.company,
        employment_type=exp.employment_type,
        location=exp.location,
        start_month=exp.start_month,
        start_year=exp.start_year,
        end_month=exp.end_month,
        end_year=exp.end_year,
        is_current=bool(exp.is_current),
        description=exp.description,
        created_at=exp.created_at,
    )


@router.post(
    "",
    response_model=ExperienceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a work experience",
    responses={
        401: {"description": "Not authenticated"},
    },
)
async def create_experience(
    data: ExperienceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Add a new work experience entry to the authenticated user's profile."""
    experience = Experience(
        user_id=current_user.id,
        title=data.title,
        company=data.company,
        employment_type=data.employment_type,
        location=data.location,
        start_month=data.start_month,
        start_year=data.start_year,
        end_month=None if data.is_current else data.end_month,
        end_year=None if data.is_current else data.end_year,
        is_current=1 if data.is_current else 0,
        description=data.description,
    )
    db.add(experience)
    db.commit()
    db.refresh(experience)

    return _experience_to_response(experience)


@router.patch(
    "/{experience_id}",
    response_model=ExperienceResponse,
    summary="Update a work experience",
    responses={
        401: {"description": "Not authenticated"},
        404: {"description": "Experience not found"},
    },
)
async def update_experience(
    experience_id: str,
    data: ExperienceUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    experience = db.query(Experience).filter(
        Experience.id == experience_id,
        Experience.user_id == current_user.id,
    ).first()
    if not experience:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Experience not found",
        )

    update_data = data.model_dump(exclude_unset=True)

    # Handle is_current: if set to True, clear end_month and end_year
    if update_data.get("is_current") is True:
        update_data["end_month"] = None
        update_data["end_year"] = None

    for field, value in update_data.items():
        if field == "is_current":
            setattr(experience, field, 1 if value else 0)
        else:
            setattr(experience, field, value)

    experience.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(experience)

    return _experience_to_response(experience)


@router.delete(
    "/{experience_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a work experience",
    responses={
        401: {"description": "Not authenticated"},
        404: {"description": "Experience not found"},
    },
)
async def delete_experience(
    experience_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    experience = db.query(Experience).filter(
        Experience.id == experience_id,
        Experience.user_id == current_user.id,
    ).first()
    if not experience:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Experience not found",
        )

    db.delete(experience)
    db.commit()
