from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.database.connection import get_db
from api.database.models import User, Education
from api.routes.profile.educations.schemas import EducationCreate, EducationUpdate, EducationResponse
from api.auth import get_current_user

router = APIRouter(prefix="/educations", tags=["Profile - Educations"])


def _education_to_response(edu: Education) -> EducationResponse:
    return EducationResponse(
        id=edu.id,
        institution=edu.institution,
        degree=edu.degree,
        degree_type=edu.degree_type,
        field_of_study=edu.field_of_study,
        start_year=edu.start_year,
        end_year=edu.end_year,
        is_current=bool(edu.is_current),
        description=edu.description,
        created_at=edu.created_at,
    )


@router.post("", response_model=EducationResponse, status_code=status.HTTP_201_CREATED)
async def create_education(
    data: EducationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    education = Education(
        user_id=current_user.id,
        institution=data.institution,
        degree=data.degree,
        degree_type=data.degree_type,
        field_of_study=data.field_of_study,
        start_year=data.start_year,
        end_year=None if data.is_current else data.end_year,
        is_current=1 if data.is_current else 0,
        description=data.description,
    )
    db.add(education)
    db.commit()
    db.refresh(education)

    return _education_to_response(education)


@router.patch("/{education_id}", response_model=EducationResponse)
async def update_education(
    education_id: str,
    data: EducationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    education = db.query(Education).filter(
        Education.id == education_id,
        Education.user_id == current_user.id,
    ).first()
    if not education:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Education not found",
        )

    update_data = data.model_dump(exclude_unset=True)

    # Handle is_current: if set to True, clear end_year
    if update_data.get("is_current") is True:
        update_data["end_year"] = None

    for field, value in update_data.items():
        if field == "is_current":
            setattr(education, field, 1 if value else 0)
        else:
            setattr(education, field, value)

    education.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(education)

    return _education_to_response(education)


@router.delete("/{education_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_education(
    education_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    education = db.query(Education).filter(
        Education.id == education_id,
        Education.user_id == current_user.id,
    ).first()
    if not education:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Education not found",
        )

    db.delete(education)
    db.commit()
