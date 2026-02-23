from __future__ import annotations

import json
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.database.connection import get_db
from api.database.models import User, Experience, Education
from api.schemas.profile import ProfileUpdate, ProfileResponse
from api.schemas.experience import ExperienceCreate, ExperienceUpdate, ExperienceResponse
from api.schemas.education import EducationCreate, EducationUpdate, EducationResponse
from api.auth import get_current_user
from api.utils import safe_parse_json_list

router = APIRouter(prefix="/profile", tags=["Profile"])


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


def _build_profile_response(user: User, experiences: list[Experience], educations: list[Education]) -> ProfileResponse:
    return ProfileResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        phone=user.phone,
        bio=user.bio,
        location=user.location,
        experience_level=user.experience_level,
        experience_years=user.experience_years,
        current_role=user.current_role,
        skills=safe_parse_json_list(user.skills_json),
        availability_status=user.availability_status or "available",
        reskilling_status=user.reskilling_status,
        adopted_by_company=user.adopted_by_company,
        linkedin_url=user.linkedin_url,
        github_url=user.github_url,
        portfolio_url=user.portfolio_url,
        experiences=[_experience_to_response(exp) for exp in experiences],
        educations=[_education_to_response(edu) for edu in educations],
        created_at=user.created_at,
    )


# --- Profile endpoints ---

@router.get("", response_model=ProfileResponse)
async def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    experiences = db.query(Experience).filter(
        Experience.user_id == current_user.id,
    ).order_by(Experience.start_year.desc()).all()

    educations = db.query(Education).filter(
        Education.user_id == current_user.id,
    ).order_by(Education.start_year.desc()).all()

    return _build_profile_response(current_user, experiences, educations)


@router.patch("", response_model=ProfileResponse)
async def update_profile(
    data: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    update_data = data.model_dump(exclude_unset=True)

    # Special handling: convert skills list to JSON string for skills_json column
    if "skills" in update_data:
        skills = update_data.pop("skills")
        current_user.skills_json = json.dumps(skills) if skills is not None else "[]"

    for field, value in update_data.items():
        setattr(current_user, field, value)

    current_user.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(current_user)

    experiences = db.query(Experience).filter(
        Experience.user_id == current_user.id,
    ).order_by(Experience.start_year.desc()).all()

    educations = db.query(Education).filter(
        Education.user_id == current_user.id,
    ).order_by(Education.start_year.desc()).all()

    return _build_profile_response(current_user, experiences, educations)


# --- Experience endpoints ---

@router.post("/experiences", response_model=ExperienceResponse, status_code=status.HTTP_201_CREATED)
async def create_experience(
    data: ExperienceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
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


@router.patch("/experiences/{experience_id}", response_model=ExperienceResponse)
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


@router.delete("/experiences/{experience_id}", status_code=status.HTTP_204_NO_CONTENT)
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


# --- Education endpoints ---

@router.post("/educations", response_model=EducationResponse, status_code=status.HTTP_201_CREATED)
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


@router.patch("/educations/{education_id}", response_model=EducationResponse)
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


@router.delete("/educations/{education_id}", status_code=status.HTTP_204_NO_CONTENT)
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
