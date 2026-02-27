from __future__ import annotations

from typing import Literal, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from api.database.connection import get_db
from api.database.models import User, Experience, Education
from api.routes.talents.schemas import TalentCardResponse, TalentCardListResponse, TalentDetailResponse
from api.routes.profile.experiences.router import _experience_to_response
from api.routes.profile.educations.router import _education_to_response
from api.utils import safe_parse_json_list

router = APIRouter(prefix="/talents", tags=["Talents"])


def _escape_ilike(value: str) -> str:
    """Escape ILIKE wildcards (%, _) in user input to prevent unintended pattern matching."""
    return value.replace("%", r"\%").replace("_", r"\_")


@router.get(
    "",
    response_model=TalentCardListResponse,
    summary="Browse the talent directory",
    openapi_extra={"security": []},
)
async def list_talents(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    search: Optional[str] = None,
    skills: Optional[str] = None,
    availability: Optional[str] = None,
    experience_level: Optional[str] = None,
    location: Optional[str] = None,
    ai_readiness: Optional[Literal["beginner", "intermediate", "advanced", "expert"]] = None,
    db: Session = Depends(get_db),
):
    """List public talents with search, filters, and pagination.

    Only returns users where is_public=1 AND is_active=1.
    No authentication required.
    """
    query = db.query(User).filter(User.is_public == 1, User.is_active == 1, User.user_type == "talent")

    # Search across full_name, current_role, skills_json
    if search:
        escaped = _escape_ilike(search)
        search_term = f"%{escaped}%"
        query = query.filter(
            or_(
                User.full_name.ilike(search_term),
                User.current_role.ilike(search_term),
                User.skills_json.ilike(search_term),
            )
        )

    # Skills filter: OR logic with ILIKE on skills_json
    if skills:
        skill_list = [s.strip() for s in skills.split(",") if s.strip()]
        if skill_list:
            skill_conditions = [
                User.skills_json.ilike(f"%{_escape_ilike(skill)}%") for skill in skill_list
            ]
            query = query.filter(or_(*skill_conditions))

    if availability:
        query = query.filter(User.availability_status == availability)

    if experience_level:
        query = query.filter(User.experience_level == experience_level)

    if location:
        query = query.filter(User.location.ilike(f"%{_escape_ilike(location)}%"))

    if ai_readiness:
        query = query.filter(User.ai_readiness_level == ai_readiness)

    total = query.count()
    users = query.order_by(User.created_at.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()

    items = []
    for user in users:
        items.append(TalentCardResponse(
            id=user.id,
            full_name=user.full_name,
            current_role=user.current_role,
            location=user.location,
            skills=safe_parse_json_list(user.skills_json),
            experience_level=user.experience_level,
            experience_years=user.experience_years,
            availability_status=user.availability_status or "available",
            bio=user.bio,
            ai_readiness_score=user.ai_readiness_score,
            ai_readiness_level=user.ai_readiness_level,
        ))

    return TalentCardListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/{talent_id}",
    response_model=TalentDetailResponse,
    summary="Get talent profile details",
    openapi_extra={"security": []},
    responses={404: {"description": "Talent not found or profile is private"}},
)
async def get_talent(
    talent_id: str,
    db: Session = Depends(get_db),
):
    """Get a single public talent's full profile.

    Returns 404 for private users AND non-existent users (privacy: no enumeration).
    No authentication required.
    """
    user = db.query(User).filter(
        User.id == talent_id,
        User.is_public == 1,
        User.is_active == 1,
        User.user_type == "talent",
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Talent not found",
        )

    experiences = db.query(Experience).filter(
        Experience.user_id == user.id,
    ).order_by(Experience.start_year.desc()).all()

    educations = db.query(Education).filter(
        Education.user_id == user.id,
    ).order_by(Education.start_year.desc()).all()

    return TalentDetailResponse(
        id=user.id,
        full_name=user.full_name,
        bio=user.bio,
        current_role=user.current_role,
        location=user.location,
        experience_level=user.experience_level,
        experience_years=user.experience_years,
        skills=safe_parse_json_list(user.skills_json),
        availability_status=user.availability_status or "available",
        linkedin_url=user.linkedin_url,
        github_url=user.github_url,
        portfolio_url=user.portfolio_url,
        ai_readiness_score=user.ai_readiness_score,
        ai_readiness_level=user.ai_readiness_level,
        experiences=[_experience_to_response(exp) for exp in experiences],
        educations=[_education_to_response(edu) for edu in educations],
        created_at=user.created_at,
    )
