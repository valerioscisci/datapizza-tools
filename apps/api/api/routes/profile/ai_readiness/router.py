"""AI Readiness assessment endpoints.

Provides quiz metadata, submission, retrieval, and course suggestions
based on weak areas identified in the quiz.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.database.connection import get_db
from api.database.models import User, Course, AIReadinessAssessment
from api.auth import get_current_user
from api.routes.profile.ai_readiness.questions import (
    QUIZ_QUESTIONS,
    QUIZ_VERSION,
    compute_score,
    get_weak_categories,
)
from api.routes.profile.ai_readiness.schemas import (
    QuizQuestionMeta,
    QuizMetaResponse,
    QuizSubmission,
    AssessmentResponse,
    CourseSuggestion,
    SuggestionsResponse,
)

logger = structlog.get_logger()

router = APIRouter(prefix="/ai-readiness", tags=["Profile - AI Readiness"])


@router.get(
    "/quiz",
    response_model=QuizMetaResponse,
    summary="Get quiz question IDs and version",
    responses={401: {"description": "Not authenticated"}},
)
async def get_quiz(
    current_user: User = Depends(get_current_user),
):
    """Return the list of question IDs and the current quiz version.

    The frontend uses the IDs as i18n keys to render localized question text.
    """
    questions = [QuizQuestionMeta(id=q["id"]) for q in QUIZ_QUESTIONS]
    return QuizMetaResponse(questions=questions, version=QUIZ_VERSION)


@router.post(
    "",
    response_model=AssessmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit quiz answers",
    responses={
        401: {"description": "Not authenticated"},
        403: {"description": "Company users cannot take the quiz"},
        422: {"description": "Validation error in answers"},
    },
)
async def submit_quiz(
    data: QuizSubmission,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Submit quiz answers, compute score, and save assessment.

    Creates a new AIReadinessAssessment row and updates the User's
    denormalized score/level fields atomically.
    Only talent users can take the quiz; company users receive 403.
    """
    if current_user.user_type != "talent":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only talent users can take the AI readiness quiz",
        )

    percentage, level = compute_score(data.answers)

    now = datetime.now(timezone.utc)
    assessment = AIReadinessAssessment(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        answers_json=json.dumps(data.answers),
        total_score=percentage,
        readiness_level=level,
        quiz_version=QUIZ_VERSION,
        created_at=now,
    )
    db.add(assessment)

    # Update denormalized fields on User
    current_user.ai_readiness_score = percentage
    current_user.ai_readiness_level = level

    db.commit()
    db.refresh(assessment)

    logger.info(
        "ai_readiness_submitted",
        user_id=current_user.id,
        score=percentage,
        level=level,
    )

    return AssessmentResponse(
        id=assessment.id,
        total_score=assessment.total_score,
        readiness_level=assessment.readiness_level,
        answers=data.answers,
        quiz_version=assessment.quiz_version,
        created_at=assessment.created_at,
    )


@router.get(
    "",
    response_model=AssessmentResponse,
    summary="Get latest assessment",
    responses={
        401: {"description": "Not authenticated"},
        404: {"description": "No assessment found"},
    },
)
async def get_assessment(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return the current user's most recent AI readiness assessment."""
    assessment = (
        db.query(AIReadinessAssessment)
        .filter(AIReadinessAssessment.user_id == current_user.id)
        .order_by(AIReadinessAssessment.created_at.desc())
        .first()
    )

    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No AI readiness assessment found",
        )

    answers = json.loads(assessment.answers_json) if assessment.answers_json else {}

    return AssessmentResponse(
        id=assessment.id,
        total_score=assessment.total_score,
        readiness_level=assessment.readiness_level,
        answers=answers,
        quiz_version=assessment.quiz_version,
        created_at=assessment.created_at,
    )


@router.get(
    "/suggestions",
    response_model=SuggestionsResponse,
    summary="Get course suggestions based on weak areas",
    responses={
        401: {"description": "Not authenticated"},
        404: {"description": "No assessment found"},
    },
)
async def get_suggestions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return course suggestions based on the user's weak quiz categories.

    Queries the latest assessment, identifies weak categories (score < 2),
    and returns matching courses prioritizing beginner/intermediate levels.
    """
    assessment = (
        db.query(AIReadinessAssessment)
        .filter(AIReadinessAssessment.user_id == current_user.id)
        .order_by(AIReadinessAssessment.created_at.desc())
        .first()
    )

    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No AI readiness assessment found",
        )

    answers = json.loads(assessment.answers_json) if assessment.answers_json else {}
    weak_cats = get_weak_categories(answers)

    if not weak_cats:
        return SuggestionsResponse(suggestions=[], weak_categories=[])

    # Query courses matching weak categories, prioritize beginner/intermediate
    courses = (
        db.query(Course)
        .filter(
            Course.is_active == 1,
            Course.category.in_(weak_cats),
            Course.level.in_(["beginner", "intermediate"]),
        )
        .order_by(Course.level.asc(), Course.created_at.desc())
        .limit(10)
        .all()
    )

    suggestions = [
        CourseSuggestion(
            id=c.id,
            title=c.title,
            provider=c.provider,
            level=c.level,
            url=c.url,
            category=c.category,
        )
        for c in courses
    ]

    return SuggestionsResponse(suggestions=suggestions, weak_categories=weak_cats)
