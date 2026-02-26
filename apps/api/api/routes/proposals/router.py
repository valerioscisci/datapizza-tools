from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from api.database.connection import get_db
from api.database.models import User, Course, Proposal, ProposalCourse, ProposalMilestone
from api.routes.proposals.schemas import (
    ProposalCreate,
    ProposalUpdate,
    ProposalResponse,
    ProposalListResponse,
    ProposalCourseResponse,
    MilestoneResponse,
    CourseNotesUpdate,
    CompanyCourseUpdate,
)
from api.auth import get_current_user
from api.services.email_service import EmailService

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


def _compute_course_fields(pc):
    """Compute is_overdue and days_remaining for a proposal course."""
    is_overdue = False
    days_remaining = None
    if pc.deadline:
        now = datetime.now(timezone.utc)
        deadline = pc.deadline if pc.deadline.tzinfo else pc.deadline.replace(tzinfo=timezone.utc)
        if not pc.is_completed:
            delta = deadline - now
            days_remaining = delta.days
            if delta.total_seconds() < 0:
                is_overdue = True
                days_remaining = delta.days  # will be negative
        else:
            days_remaining = None
    return is_overdue, days_remaining


def _xp_for_level(level: str) -> int:
    """Return XP reward for a course level."""
    mapping = {"beginner": 100, "intermediate": 200, "advanced": 300}
    return mapping.get(level, 100)


def _build_proposal_response(
    proposal: Proposal,
    company: User,
    talent: User,
    proposal_courses: list[ProposalCourse],
    courses_map: dict[str, Course],
    milestones: list[ProposalMilestone] | None = None,
) -> ProposalResponse:
    """Build a ProposalResponse from DB objects, computing progress."""
    course_responses = []
    for pc in sorted(proposal_courses, key=lambda x: x.order):
        course = courses_map.get(pc.course_id)
        is_overdue, days_remaining = _compute_course_fields(pc)
        course_responses.append(ProposalCourseResponse(
            id=pc.id,
            course_id=pc.course_id,
            course_title=course.title if course else "Unknown",
            course_provider=course.provider if course else "Unknown",
            course_level=course.level if course else "Unknown",
            course_url=course.url if course else None,
            course_duration=course.duration if course else None,
            course_category=course.category if course else None,
            order=pc.order,
            is_completed=bool(pc.is_completed),
            completed_at=pc.completed_at,
            started_at=pc.started_at,
            talent_notes=pc.talent_notes,
            company_notes=pc.company_notes,
            deadline=pc.deadline,
            xp_earned=pc.xp_earned or 0,
            is_overdue=is_overdue,
            days_remaining=days_remaining,
        ))

    total_courses = len(proposal_courses)
    completed_courses = sum(1 for pc in proposal_courses if pc.is_completed)
    progress = completed_courses / total_courses if total_courses > 0 else 0.0

    milestone_responses = []
    if milestones:
        for m in milestones:
            milestone_responses.append(MilestoneResponse(
                id=m.id,
                milestone_type=m.milestone_type,
                title=m.title,
                description=m.description,
                xp_reward=m.xp_reward or 0,
                achieved_at=m.achieved_at,
            ))

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
        total_xp=proposal.total_xp or 0,
        milestones=milestone_responses,
        hired_at=proposal.hired_at,
        hiring_notes=proposal.hiring_notes,
        created_at=proposal.created_at,
        updated_at=proposal.updated_at,
    )


def _fetch_proposal_data(db: Session, proposal: Proposal):
    """Fetch all related data for building a proposal response."""
    company = db.query(User).filter(User.id == proposal.company_id).first()
    talent = db.query(User).filter(User.id == proposal.talent_id).first()
    proposal_courses = db.query(ProposalCourse).filter(
        ProposalCourse.proposal_id == proposal.id,
    ).all()
    course_ids = [pc.course_id for pc in proposal_courses]
    courses = db.query(Course).filter(Course.id.in_(course_ids)).all() if course_ids else []
    courses_map = {c.id: c for c in courses}
    milestones = db.query(ProposalMilestone).filter(
        ProposalMilestone.proposal_id == proposal.id,
    ).all()
    return company, talent, proposal_courses, courses_map, milestones


def _create_milestone(db: Session, proposal_id: str, milestone_type: str, title: str, description: str | None, xp_reward: int) -> ProposalMilestone:
    """Create a ProposalMilestone and return it."""
    milestone = ProposalMilestone(
        id=str(uuid.uuid4()),
        proposal_id=proposal_id,
        milestone_type=milestone_type,
        title=title,
        description=description,
        xp_reward=xp_reward,
        achieved_at=datetime.now(timezone.utc),
    )
    db.add(milestone)
    return milestone


@router.post(
    "",
    response_model=ProposalResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a training proposal",
    responses={
        400: {"description": "Validation error (self-proposal, duplicate courses, etc.)"},
        401: {"description": "Not authenticated"},
        403: {"description": "Only company accounts can create proposals"},
        404: {"description": "Talent or one or more courses not found"},
    },
)
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
        total_xp=0,
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

    # Send notification email to talent
    try:
        EmailService.send_proposal_received(db, proposal, talent, current_user)
    except Exception as e:
        logger.error("email_send_failed", error=str(e), email_type="proposal_received", proposal_id=proposal.id)

    return _build_proposal_response(proposal, current_user, talent, proposal_courses, courses_map, [])


@router.get(
    "",
    response_model=ProposalListResponse,
    summary="List my proposals",
    responses={
        401: {"description": "Not authenticated"},
    },
)
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
        company, talent, proposal_courses, courses_map, milestones = _fetch_proposal_data(db, proposal)
        items.append(_build_proposal_response(proposal, company, talent, proposal_courses, courses_map, milestones))

    return ProposalListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/{proposal_id}",
    response_model=ProposalResponse,
    summary="Get proposal details",
    responses={
        401: {"description": "Not authenticated"},
        403: {"description": "Not authorized to view this proposal"},
        404: {"description": "Proposal not found"},
    },
)
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

    company, talent, proposal_courses, courses_map, milestones = _fetch_proposal_data(db, proposal)

    return _build_proposal_response(proposal, company, talent, proposal_courses, courses_map, milestones)


@router.get(
    "/{proposal_id}/dashboard",
    response_model=ProposalResponse,
    summary="Get proposal delivery dashboard",
    responses={
        401: {"description": "Not authenticated"},
        403: {"description": "Not authorized to view this proposal"},
        404: {"description": "Proposal not found"},
    },
)
async def get_proposal_dashboard(
    proposal_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get the delivery dashboard view for a proposal. Same auth as get_proposal."""
    proposal = db.query(Proposal).filter(Proposal.id == proposal_id).first()
    if not proposal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proposal not found",
        )

    user_type = current_user.user_type or "talent"

    if proposal.company_id != current_user.id and proposal.talent_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proposal not found",
        )

    if user_type != "company" and proposal.status == "draft":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proposal not found",
        )

    company, talent, proposal_courses, courses_map, milestones = _fetch_proposal_data(db, proposal)

    return _build_proposal_response(proposal, company, talent, proposal_courses, courses_map, milestones)


@router.patch(
    "/{proposal_id}",
    response_model=ProposalResponse,
    summary="Update proposal status or details",
    responses={
        401: {"description": "Not authenticated"},
        403: {"description": "Not authorized to update this proposal"},
        404: {"description": "Proposal not found"},
    },
)
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
            # Company can: draft -> sent, accepted -> hired, completed -> hired
            valid_transitions = [
                ("draft", "sent"),
                ("accepted", "hired"),
                ("completed", "hired"),
            ]
            if (proposal.status, new_status) not in valid_transitions:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid status transition",
                )

            # Handle hiring
            if new_status == "hired":
                proposal.hired_at = datetime.now(timezone.utc)
                if "hiring_notes" in update_data:
                    proposal.hiring_notes = update_data["hiring_notes"]
                # Update talent user
                talent = db.query(User).filter(User.id == proposal.talent_id).first()
                if talent:
                    company = db.query(User).filter(User.id == proposal.company_id).first()
                    talent.availability_status = "employed"
                    talent.adopted_by_company = company.company_name if company else None
                logger.info("proposal_hired", proposal_id=proposal.id)

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
        if field != "hiring_notes":  # hiring_notes already handled above
            setattr(proposal, field, value)

    proposal.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(proposal)

    company, talent, proposal_courses, courses_map, milestones = _fetch_proposal_data(db, proposal)

    logger.info("proposal_updated", proposal_id=proposal.id, new_status=proposal.status)

    # Send notification emails based on status change (reuse company/talent from _fetch_proposal_data)
    try:
        if talent and company:
            if proposal.status == "accepted":
                EmailService.send_proposal_accepted(db, proposal, talent, company)
            elif proposal.status == "rejected":
                EmailService.send_proposal_rejected(db, proposal, talent, company)
            elif proposal.status == "hired":
                EmailService.send_hiring_confirmation(db, proposal, talent, company)
    except Exception as e:
        logger.error("email_send_failed", error=str(e), email_type="proposal_status_update", proposal_id=proposal.id)

    return _build_proposal_response(proposal, company, talent, proposal_courses, courses_map, milestones)


@router.patch(
    "/{proposal_id}/courses/{course_id}",
    response_model=ProposalResponse,
    summary="Mark a proposal course as completed",
    responses={
        401: {"description": "Not authenticated"},
        403: {"description": "Only talents can mark courses as completed"},
        404: {"description": "Proposal or course not found"},
    },
)
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

    now = datetime.now(timezone.utc)
    proposal_course.is_completed = 1
    proposal_course.completed_at = now

    # XP based on course level
    course = db.query(Course).filter(Course.id == course_id).first()
    course_level = course.level if course else "beginner"
    xp = _xp_for_level(course_level)
    proposal_course.xp_earned = xp

    # Create course_completed milestone
    _create_milestone(
        db, proposal.id, "course_completed",
        f"Corso completato: {course.title if course else 'Unknown'}",
        None, xp,
    )

    # Check all courses for progress milestones
    all_proposal_courses = db.query(ProposalCourse).filter(
        ProposalCourse.proposal_id == proposal_id,
    ).all()

    total_courses = len(all_proposal_courses)
    completed_courses = sum(1 for pc in all_proposal_courses if pc.is_completed or pc.id == proposal_course.id)

    # Existing milestones for this proposal
    existing_milestones = db.query(ProposalMilestone).filter(
        ProposalMilestone.proposal_id == proposal.id,
    ).all()
    existing_types = {m.milestone_type for m in existing_milestones}

    # Progress milestones
    if total_courses > 0:
        progress_pct = completed_courses / total_courses
        thresholds = [
            (0.25, "25_percent", "25% completato"),
            (0.50, "50_percent", "50% completato"),
            (0.75, "75_percent", "75% completato"),
            (1.00, "all_complete", "Percorso completato al 100%"),
        ]
        for threshold, mtype, title in thresholds:
            if progress_pct >= threshold and mtype not in existing_types:
                _create_milestone(db, proposal.id, mtype, title, None, 50)
                xp += 50

    # Streak: 3 consecutive completed courses by order
    sorted_pcs = sorted(all_proposal_courses, key=lambda x: x.order)
    consecutive = 0
    for pc in sorted_pcs:
        if pc.is_completed or pc.id == proposal_course.id:
            consecutive += 1
        else:
            consecutive = 0
    if consecutive >= 3 and "streak_3" not in existing_types:
        _create_milestone(db, proposal.id, "streak_3", "Streak di 3 corsi completati!", None, 100)
        xp += 100

    # Auto-complete proposal if all courses done
    all_completed = all(pc.is_completed or pc.id == proposal_course.id for pc in all_proposal_courses)
    if all_completed:
        proposal.status = "completed"
        proposal.updated_at = now
        logger.info("proposal_auto_completed", proposal_id=proposal.id)

    # Update total_xp
    proposal.total_xp = (proposal.total_xp or 0) + xp

    db.commit()
    db.refresh(proposal)

    company, talent, proposal_courses_all, courses_map, milestones = _fetch_proposal_data(db, proposal)

    logger.info("proposal_course_completed", proposal_id=proposal.id, course_id=course_id)

    # Send notification emails for course completion and milestones (reuse company/talent from _fetch_proposal_data)
    try:
        if talent and company:
            course_title = course.title if course else "Unknown"
            EmailService.send_course_completed(db, proposal, course_title, talent, company)
            # Notify talent about milestone XP earned
            if xp > 0:
                EmailService.send_milestone_reached(db, proposal, "course_completed", xp, talent)
    except Exception as e:
        logger.error("email_send_failed", error=str(e), email_type="course_completed", proposal_id=proposal.id)

    return _build_proposal_response(proposal, company, talent, proposal_courses_all, courses_map, milestones)


@router.patch(
    "/{proposal_id}/courses/{course_id}/start",
    response_model=ProposalResponse,
    summary="Start a proposal course",
    responses={
        401: {"description": "Not authenticated"},
        403: {"description": "Only talents can start courses"},
        404: {"description": "Proposal or course not found"},
    },
)
async def start_proposal_course(
    proposal_id: str,
    course_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Mark a course as started. Talent only, proposal must be accepted."""
    user_type = current_user.user_type or "talent"

    if user_type == "company":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only talents can start courses",
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
            detail="Proposal must be accepted to start courses",
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

    if proposal_course.started_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Course already started",
        )

    now = datetime.now(timezone.utc)
    proposal_course.started_at = now

    # Milestone: course_started (10 XP)
    xp_total = 10
    _create_milestone(
        db, proposal.id, "course_started",
        "Corso iniziato",
        None, 10,
    )

    # Check if this is the very first course started in this proposal
    all_pcs = db.query(ProposalCourse).filter(
        ProposalCourse.proposal_id == proposal_id,
    ).all()
    started_count = sum(1 for pc in all_pcs if pc.started_at or pc.id == proposal_course.id)
    if started_count == 1:
        _create_milestone(
            db, proposal.id, "first_course",
            "Primo corso iniziato!",
            "Bonus per aver iniziato il percorso formativo",
            25,
        )
        xp_total += 25

    proposal.total_xp = (proposal.total_xp or 0) + xp_total

    db.commit()
    db.refresh(proposal)

    company, talent, proposal_courses_all, courses_map, milestones = _fetch_proposal_data(db, proposal)

    logger.info("proposal_course_started", proposal_id=proposal.id, course_id=course_id)

    # Send notification email for course start (reuse company/talent from _fetch_proposal_data)
    try:
        if talent and company:
            course_title = courses_map.get(course_id)
            course_title = course_title.title if course_title else "Unknown"
            EmailService.send_course_started(db, proposal, course_title, talent, company)
    except Exception as e:
        logger.error("email_send_failed", error=str(e), email_type="course_started", proposal_id=proposal.id)

    return _build_proposal_response(proposal, company, talent, proposal_courses_all, courses_map, milestones)


@router.patch(
    "/{proposal_id}/courses/{course_id}/notes",
    response_model=ProposalResponse,
    summary="Update talent notes on a course",
    responses={
        401: {"description": "Not authenticated"},
        403: {"description": "Only talents can update course notes"},
        404: {"description": "Proposal or course not found"},
    },
)
async def update_course_notes(
    proposal_id: str,
    course_id: str,
    data: CourseNotesUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update talent notes on a proposal course. Talent only."""
    user_type = current_user.user_type or "talent"

    if user_type == "company":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only talents can update course notes",
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

    if proposal.status not in ("accepted", "completed", "hired"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Proposal must be accepted, completed, or hired to update notes",
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

    if data.talent_notes is not None:
        proposal_course.talent_notes = data.talent_notes

    db.commit()
    db.refresh(proposal)

    company, talent, proposal_courses_all, courses_map, milestones = _fetch_proposal_data(db, proposal)

    return _build_proposal_response(proposal, company, talent, proposal_courses_all, courses_map, milestones)


@router.patch(
    "/{proposal_id}/courses/{course_id}/company-update",
    response_model=ProposalResponse,
    summary="Update company notes and deadline on a course",
    responses={
        401: {"description": "Not authenticated"},
        403: {"description": "Only companies can update company course details"},
        404: {"description": "Proposal or course not found"},
    },
)
async def update_course_company(
    proposal_id: str,
    course_id: str,
    data: CompanyCourseUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update company notes and/or deadline on a proposal course. Company only."""
    user_type = current_user.user_type or "talent"

    if user_type != "company":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only companies can update company course details",
        )

    proposal = db.query(Proposal).filter(Proposal.id == proposal_id).first()
    if not proposal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proposal not found",
        )

    if proposal.company_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this proposal",
        )

    if proposal.status not in ("accepted", "completed", "hired"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Proposal must be accepted, completed, or hired to update company details",
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

    if data.company_notes is not None:
        proposal_course.company_notes = data.company_notes
    if data.deadline is not None:
        proposal_course.deadline = data.deadline

    db.commit()
    db.refresh(proposal)

    company, talent, proposal_courses_all, courses_map, milestones = _fetch_proposal_data(db, proposal)

    return _build_proposal_response(proposal, company, talent, proposal_courses_all, courses_map, milestones)
