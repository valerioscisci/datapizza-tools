from __future__ import annotations

import json
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from api.database.connection import get_db
from api.database.models import User, Experience, Education
from api.routes.profile.schemas import ProfileUpdate, ProfileResponse
from api.routes.profile.experiences.router import _experience_to_response
from api.routes.profile.experiences.schemas import ExperienceResponse
from api.routes.profile.educations.router import _education_to_response
from api.routes.profile.educations.schemas import EducationResponse
from api.auth import get_current_user
from api.utils import safe_parse_json_list

router = APIRouter(prefix="/profile", tags=["Profile"])


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
        user_type=user.user_type or "talent",
        company_name=user.company_name,
        company_website=user.company_website,
        company_size=user.company_size,
        industry=user.industry,
        is_public=bool(user.is_public),
        experiences=[_experience_to_response(exp) for exp in experiences],
        educations=[_education_to_response(edu) for edu in educations],
        created_at=user.created_at,
    )


# --- Profile endpoints ---

@router.get(
    "",
    response_model=ProfileResponse,
    summary="Get my profile",
    responses={
        401: {"description": "Not authenticated"},
    },
)
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


@router.patch(
    "",
    response_model=ProfileResponse,
    summary="Update my profile",
    responses={
        401: {"description": "Not authenticated"},
    },
)
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

    # Special handling: convert is_public bool to Integer for SQLite
    if "is_public" in update_data:
        is_public = update_data.pop("is_public")
        current_user.is_public = 1 if is_public else 0

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
