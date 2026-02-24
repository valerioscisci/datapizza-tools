from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from api.database.connection import get_db
from api.database.models import User, Course, Proposal, ProposalCourse
from api.routes.proposals.schemas import (
    ProposalCreate,
    ProposalUpdate,
    ProposalResponse,
    ProposalListResponse,
    ProposalCourseResponse,
)
from api.auth import get_current_user

logger = structlog.get_logger()

router = APIRouter(prefix="/proposals", tags=["Proposals"])


async def get_current_company_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Dependency that ensures the current user is a company account."""
    if (current_user.user_type or "talent") != "company":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only company accounts can perform this action",
        )
    return current_user


def _build_proposal_response(
    proposal: Proposal,
    company: User,
    talent: User,
    proposal_courses: list[ProposalCourse],
    courses_map: dict[str, Course],
) -> ProposalResponse:
    """Build a ProposalResponse from DB objects, computing progress."""
    course_responses = []
    for pc in sorted(proposal_courses, key=lambda x: x.order):
        course = courses_map.get(pc.course_id)
        course_responses.append(ProposalCourseResponse(
            id=pc.id,
            course_id=pc.course_id,
            course_title=course.title if course else "Unknown",
            course_provider=course.provider if course else "Unknown",
            course_level=course.level if course else "Unknown",
            order=pc.order,
            is_completed=bool(pc.is_completed),
            completed_at=pc.completed_at,
        ))

    total_courses = len(proposal_courses)
    completed_courses = sum(1 for pc in proposal_courses if pc.is_completed)
    progress = completed_courses / total_courses if total_courses > 0 else 0.0

    return ProposalResponse(
        id=proposal.id,
        company_id=proposal.company_id,
        company_name=(company.company_name or company.full_name) if company else "Unknown",
        talent_id=proposal.talent_id,
        talent_name=talent.full_name if talent else "Unknown",
        status=proposal.status,
        message=proposal.message,
        budget_range=proposal.budget_range,
        courses=course_responses,
        progress=progress,
        created_at=proposal.created_at,
        updated_at=proposal.updated_at,
    )


@router.post("", response_model=ProposalResponse, status_code=status.HTTP_201_CREATED)
async def create_proposal(
    data: ProposalCreate,
    current_user: User = Depends(get_current_company_user),
    db: Session = Depends(get_db),
):
    """Company creates a proposal for a talent with a list of courses."""
    # Prevent self-proposals
    if data.talent_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot create a proposal for yourself",
        )

    # Reject duplicate course_ids
    if len(data.course_ids) != len(set(data.course_ids)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Duplicate course_ids are not allowed",
        )

    # Validate talent exists, is public, active, and is a talent (not a company)
    talent = db.query(User).filter(
        User.id == data.talent_id,
        User.is_public == 1,
        User.is_active == 1,
        User.user_type == "talent",
    ).first()
    if not talent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Talent not found",
        )

    # Validate all course_ids exist and are active
    unique_course_ids = list(set(data.course_ids))
    courses = db.query(Course).filter(
        Course.id.in_(unique_course_ids),
        Course.is_active == 1,
    ).all()
    if len(courses) != len(unique_course_ids):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="One or more courses not found",
        )

    # Create proposal
    now = datetime.now(timezone.utc)
    proposal = Proposal(
        id=str(uuid.uuid4()),
        company_id=current_user.id,
        talent_id=data.talent_id,
        status="sent",
        message=data.message,
        budget_range=data.budget_range,
        created_at=now,
        updated_at=now,
    )
    db.add(proposal)
    db.flush()  # Ensure proposal.id is available for courses

    # Create ProposalCourse rows preserving order
    proposal_courses = []
    courses_map = {c.id: c for c in courses}
    for idx, course_id in enumerate(data.course_ids):
        pc = ProposalCourse(
            id=str(uuid.uuid4()),
            proposal_id=proposal.id,
            course_id=course_id,
            order=idx,
        )
        db.add(pc)
        proposal_courses.append(pc)

    db.commit()
    db.refresh(proposal)

    logger.info("proposal_created", proposal_id=proposal.id, company_id=current_user.id, talent_id=data.talent_id)

    return _build_proposal_response(proposal, current_user, talent, proposal_courses, courses_map)


@router.get("", response_model=ProposalListResponse)
async def list_proposals(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    proposal_status: Optional[str] = Query(None, alias="status"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List proposals for the current user (company or talent)."""
    user_type = current_user.user_type or "talent"

    if user_type == "company":
        query = db.query(Proposal).filter(Proposal.company_id == current_user.id)
    else:
        # Talents don't see drafts
        query = db.query(Proposal).filter(
            Proposal.talent_id == current_user.id,
            Proposal.status != "draft",
        )

    if proposal_status:
        query = query.filter(Proposal.status == proposal_status)

    total = query.count()
    proposals = query.order_by(Proposal.created_at.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()

    items = []
    for proposal in proposals:
        company = db.query(User).filter(User.id == proposal.company_id).first()
        talent = db.query(User).filter(User.id == proposal.talent_id).first()
        proposal_courses = db.query(ProposalCourse).filter(
            ProposalCourse.proposal_id == proposal.id,
        ).all()
        course_ids = [pc.course_id for pc in proposal_courses]
        courses = db.query(Course).filter(Course.id.in_(course_ids)).all() if course_ids else []
        courses_map = {c.id: c for c in courses}

        items.append(_build_proposal_response(proposal, company, talent, proposal_courses, courses_map))

    return ProposalListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{proposal_id}", response_model=ProposalResponse)
async def get_proposal(
    proposal_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get proposal detail. Must be company owner or talent recipient."""
    proposal = db.query(Proposal).filter(Proposal.id == proposal_id).first()
    if not proposal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proposal not found",
        )

    user_type = current_user.user_type or "talent"

    # Auth: must be company owner or talent recipient
    if proposal.company_id != current_user.id and proposal.talent_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proposal not found",
        )

    # Talents can't see drafts
    if user_type != "company" and proposal.status == "draft":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proposal not found",
        )

    company = db.query(User).filter(User.id == proposal.company_id).first()
    talent = db.query(User).filter(User.id == proposal.talent_id).first()
    proposal_courses = db.query(ProposalCourse).filter(
        ProposalCourse.proposal_id == proposal.id,
    ).all()
    course_ids = [pc.course_id for pc in proposal_courses]
    courses = db.query(Course).filter(Course.id.in_(course_ids)).all() if course_ids else []
    courses_map = {c.id: c for c in courses}

    return _build_proposal_response(proposal, company, talent, proposal_courses, courses_map)


@router.patch("/{proposal_id}", response_model=ProposalResponse)
async def update_proposal(
    proposal_id: str,
    data: ProposalUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a proposal. Rules depend on user type and current status."""
    proposal = db.query(Proposal).filter(Proposal.id == proposal_id).first()
    if not proposal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proposal not found",
        )

    user_type = current_user.user_type or "talent"
    update_data = data.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update",
        )

    if user_type == "company":
        # Company must own the proposal
        if proposal.company_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this proposal",
            )

        new_status = update_data.get("status")
        if new_status:
            # Company can only: draft -> sent
            if not (proposal.status == "draft" and new_status == "sent"):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid status transition",
                )

        # Company can only update message/budget on draft proposals
        if proposal.status != "draft" and ("message" in update_data or "budget_range" in update_data):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Can only update message/budget on draft proposals",
            )

    else:
        # Talent must be the recipient
        if proposal.talent_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this proposal",
            )

        new_status = update_data.get("status")
        if new_status:
            # Talent can only: sent -> accepted/rejected
            if not (proposal.status == "sent" and new_status in ("accepted", "rejected")):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid status transition",
                )
            # Talent can only change status, not message/budget
            update_data = {"status": new_status}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Talents can only update the status of a proposal",
            )

    for field, value in update_data.items():
        setattr(proposal, field, value)

    proposal.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(proposal)

    company = db.query(User).filter(User.id == proposal.company_id).first()
    talent = db.query(User).filter(User.id == proposal.talent_id).first()
    proposal_courses = db.query(ProposalCourse).filter(
        ProposalCourse.proposal_id == proposal.id,
    ).all()
    course_ids = [pc.course_id for pc in proposal_courses]
    courses = db.query(Course).filter(Course.id.in_(course_ids)).all() if course_ids else []
    courses_map = {c.id: c for c in courses}

    logger.info("proposal_updated", proposal_id=proposal.id, new_status=proposal.status)

    return _build_proposal_response(proposal, company, talent, proposal_courses, courses_map)


@router.patch("/{proposal_id}/courses/{course_id}", response_model=ProposalResponse)
async def complete_proposal_course(
    proposal_id: str,
    course_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Mark a course as completed in a proposal. Talent only, proposal must be accepted."""
    user_type = current_user.user_type or "talent"

    if user_type == "company":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only talents can mark courses as completed",
        )

    proposal = db.query(Proposal).filter(Proposal.id == proposal_id).first()
    if not proposal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proposal not found",
        )

    if proposal.talent_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this proposal",
        )

    if proposal.status != "accepted":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Proposal must be accepted to complete courses",
        )

    proposal_course = db.query(ProposalCourse).filter(
        ProposalCourse.proposal_id == proposal_id,
        ProposalCourse.course_id == course_id,
    ).first()
    if not proposal_course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found in this proposal",
        )

    if proposal_course.is_completed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Course already completed",
        )

    proposal_course.is_completed = 1
    proposal_course.completed_at = datetime.now(timezone.utc)

    # Check if all courses are completed -> auto-complete proposal
    all_proposal_courses = db.query(ProposalCourse).filter(
        ProposalCourse.proposal_id == proposal_id,
    ).all()

    all_completed = all(pc.is_completed or pc.id == proposal_course.id for pc in all_proposal_courses)
    if all_completed:
        proposal.status = "completed"
        proposal.updated_at = datetime.now(timezone.utc)
        logger.info("proposal_auto_completed", proposal_id=proposal.id)

    db.commit()
    db.refresh(proposal)

    company = db.query(User).filter(User.id == proposal.company_id).first()
    talent = db.query(User).filter(User.id == proposal.talent_id).first()
    proposal_courses_all = db.query(ProposalCourse).filter(
        ProposalCourse.proposal_id == proposal.id,
    ).all()
    c_ids = [pc.course_id for pc in proposal_courses_all]
    courses = db.query(Course).filter(Course.id.in_(c_ids)).all() if c_ids else []
    courses_map = {c.id: c for c in courses}

    logger.info("proposal_course_completed", proposal_id=proposal.id, course_id=course_id)

    return _build_proposal_response(proposal, company, talent, proposal_courses_all, courses_map)
