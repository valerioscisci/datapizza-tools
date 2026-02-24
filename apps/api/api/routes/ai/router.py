"""AI-powered job matching and career recommendations routes.

Provides endpoints for generating and retrieving AI-powered job matches
and career advice using Gemini, with 24-hour caching in the AICache table.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timedelta, timezone

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.database.connection import get_db
from api.database.models import User, Job, Course, News, AICache, Experience
from api.routes.ai.schemas import (
    JobMatchResponse,
    JobMatchItem,
    CareerAdviceResponse,
    RecommendedCourse,
    RecommendedArticle,
)
from api.auth import get_current_user
from api.services.ai_advisor import get_advisor
from api.utils import safe_parse_json_list

logger = structlog.get_logger()

router = APIRouter(prefix="/ai", tags=["AI"])

CACHE_TTL_HOURS = 24


def _build_user_profile_dict(user: User, experiences: list[Experience]) -> dict:
    """Build a user profile dict for AI prompt consumption."""
    skills = safe_parse_json_list(user.skills_json)
    experiences_summary = []
    for exp in experiences:
        exp_item = {
            "title": exp.title,
            "company": exp.company,
            "start_year": exp.start_year,
            "end_year": exp.end_year,
            "is_current": bool(exp.is_current),
        }
        if exp.description:
            exp_item["description"] = exp.description
        experiences_summary.append(exp_item)

    return {
        "skills": skills,
        "experience_level": user.experience_level,
        "experience_years": user.experience_years,
        "current_role": user.current_role,
        "location": user.location,
        "availability_status": user.availability_status,
        "bio": user.bio,
        "experiences": experiences_summary,
    }


def _build_jobs_list(jobs: list[Job]) -> list[dict]:
    """Build a list of job dicts for AI prompt consumption."""
    result = []
    for job in jobs:
        result.append({
            "job_id": job.id,
            "title": job.title,
            "company": job.company,
            "location": job.location,
            "work_mode": job.work_mode,
            "tags": safe_parse_json_list(job.tags_json),
            "experience_level": job.experience_level,
            "description": job.description[:300] if job.description else "",
        })
    return result


def _build_courses_list(courses: list[Course]) -> list[dict]:
    """Build a list of course dicts for AI prompt consumption."""
    result = []
    for course in courses:
        result.append({
            "course_id": course.id,
            "title": course.title,
            "provider": course.provider,
            "level": course.level,
            "category": course.category,
        })
    return result


def _build_news_list(news_items: list[News]) -> list[dict]:
    """Build a list of news dicts for AI prompt consumption."""
    result = []
    for news in news_items:
        result.append({
            "news_id": news.id,
            "title": news.title,
            "category": news.category,
            "summary": news.summary[:200] if news.summary else "",
        })
    return result


def _get_valid_cache(db: Session, user_id: str, cache_type: str) -> AICache | None:
    """Get a valid (non-expired) cache entry for the given user and type."""
    cache = (
        db.query(AICache)
        .filter(AICache.user_id == user_id, AICache.cache_type == cache_type)
        .order_by(AICache.created_at.desc())
        .first()
    )
    if cache is None:
        return None

    # Handle naive datetime from SQLite (learning #26)
    expires_at = cache.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    now = datetime.now(timezone.utc)
    if expires_at < now:
        return None

    return cache


def _save_cache(
    db: Session,
    user_id: str,
    cache_type: str,
    content: dict | list,
    model_used: str | None,
) -> AICache:
    """Save a new cache entry, replacing any existing one for this user/type."""
    # Delete old cache entries for this user/type
    db.query(AICache).filter(
        AICache.user_id == user_id, AICache.cache_type == cache_type
    ).delete()

    now = datetime.now(timezone.utc)
    cache = AICache(
        id=str(uuid.uuid4()),
        user_id=user_id,
        cache_type=cache_type,
        content_json=json.dumps(content, ensure_ascii=False, default=str),
        model_used=model_used,
        created_at=now,
        expires_at=now + timedelta(hours=CACHE_TTL_HOURS),
    )
    db.add(cache)
    db.commit()
    db.refresh(cache)
    return cache


# --- POST /ai/job-matches ---


@router.post("/job-matches", response_model=JobMatchResponse)
async def generate_job_matches(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Generate AI job match scores for the current user."""
    advisor = get_advisor()
    if not advisor.is_available:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service is currently unavailable",
        )

    # Fetch user experiences
    experiences = (
        db.query(Experience)
        .filter(Experience.user_id == current_user.id)
        .order_by(Experience.start_year.desc())
        .all()
    )

    # Build profile dict
    profile_dict = _build_user_profile_dict(current_user, experiences)

    # Fetch active jobs (capped at 100 to avoid context window overflow)
    jobs = db.query(Job).filter(Job.is_active == 1).limit(100).all()
    if not jobs:
        # No jobs to match against — return empty result
        now = datetime.now(timezone.utc)
        return JobMatchResponse(matches=[], generated_at=now, model_used=advisor.model_name)

    jobs_list = _build_jobs_list(jobs)

    # Call Gemini
    matches_raw = advisor.match_jobs(profile_dict, jobs_list)
    if matches_raw is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service failed to generate matches",
        )

    # Cache the result
    cache = _save_cache(db, current_user.id, "job_matches", matches_raw, advisor.model_name)

    # Handle naive datetime from SQLite
    created_at = cache.created_at
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)

    match_items = [
        JobMatchItem(
            job_id=m["job_id"],
            score=max(0, min(100, m.get("score", 0))),
            reasons=m.get("reasons", []),
        )
        for m in matches_raw
    ]

    return JobMatchResponse(
        matches=match_items,
        generated_at=created_at,
        model_used=cache.model_used,
    )


# --- GET /ai/job-matches ---


@router.get("/job-matches", response_model=JobMatchResponse)
async def get_cached_job_matches(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get cached AI job matches for the current user."""
    cache = _get_valid_cache(db, current_user.id, "job_matches")
    if cache is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No cached job matches found. Generate new matches first.",
        )

    content = json.loads(cache.content_json)
    match_items = [
        JobMatchItem(
            job_id=m["job_id"],
            score=max(0, min(100, m.get("score", 0))),
            reasons=m.get("reasons", []),
        )
        for m in content
    ]

    # Handle naive datetime from SQLite
    created_at = cache.created_at
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)

    return JobMatchResponse(
        matches=match_items,
        generated_at=created_at,
        model_used=cache.model_used,
    )


# --- POST /ai/career-advice ---


@router.post("/career-advice", response_model=CareerAdviceResponse)
async def generate_career_advice(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Generate AI career recommendations for the current user."""
    advisor = get_advisor()
    if not advisor.is_available:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service is currently unavailable",
        )

    # Fetch user experiences
    experiences = (
        db.query(Experience)
        .filter(Experience.user_id == current_user.id)
        .order_by(Experience.start_year.desc())
        .all()
    )

    # Build profile dict
    profile_dict = _build_user_profile_dict(current_user, experiences)

    # Get job matches (from cache or generate new)
    top_jobs_data = []
    cache = _get_valid_cache(db, current_user.id, "job_matches")
    if cache:
        matches = json.loads(cache.content_json)
        # Sort by score descending, take top 5
        matches.sort(key=lambda m: m.get("score", 0), reverse=True)
        top_job_ids = [m["job_id"] for m in matches[:5]]
        if top_job_ids:
            top_jobs_db = db.query(Job).filter(Job.id.in_(top_job_ids), Job.is_active == 1).all()
            top_jobs_data = _build_jobs_list(top_jobs_db)
    else:
        # Generate job matches first
        jobs = db.query(Job).filter(Job.is_active == 1).limit(100).all()
        if jobs:
            jobs_list = _build_jobs_list(jobs)
            matches_raw = advisor.match_jobs(profile_dict, jobs_list)
            if matches_raw:
                _save_cache(db, current_user.id, "job_matches", matches_raw, advisor.model_name)
                matches_raw.sort(key=lambda m: m.get("score", 0), reverse=True)
                top_job_ids = [m["job_id"] for m in matches_raw[:5]]
                if top_job_ids:
                    top_jobs_db = db.query(Job).filter(Job.id.in_(top_job_ids), Job.is_active == 1).all()
                    top_jobs_data = _build_jobs_list(top_jobs_db)

    # Fetch courses and news
    courses = db.query(Course).filter(Course.is_active == 1).all()
    courses_list = _build_courses_list(courses)

    news_items = (
        db.query(News)
        .filter(News.is_active == 1)
        .order_by(News.published_at.desc())
        .limit(20)
        .all()
    )
    news_list = _build_news_list(news_items)

    # Call Gemini
    advice_raw = advisor.career_recommendations(profile_dict, top_jobs_data, courses_list, news_list)
    if advice_raw is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service failed to generate career advice",
        )

    # Cache the result
    cache = _save_cache(db, current_user.id, "career_advice", advice_raw, advisor.model_name)

    # Handle naive datetime from SQLite
    created_at = cache.created_at
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)

    return CareerAdviceResponse(
        career_direction=advice_raw.get("career_direction", ""),
        recommended_courses=[
            RecommendedCourse(**c) for c in advice_raw.get("recommended_courses", [])
        ],
        recommended_articles=[
            RecommendedArticle(**a) for a in advice_raw.get("recommended_articles", [])
        ],
        skill_gaps=advice_raw.get("skill_gaps", []),
        generated_at=created_at,
        model_used=cache.model_used,
    )


# --- GET /ai/career-advice ---


@router.get("/career-advice", response_model=CareerAdviceResponse)
async def get_cached_career_advice(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get cached AI career advice for the current user."""
    cache = _get_valid_cache(db, current_user.id, "career_advice")
    if cache is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No cached career advice found. Generate new advice first.",
        )

    content = json.loads(cache.content_json)

    # Handle naive datetime from SQLite
    created_at = cache.created_at
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)

    return CareerAdviceResponse(
        career_direction=content.get("career_direction", ""),
        recommended_courses=[
            RecommendedCourse(**c) for c in content.get("recommended_courses", [])
        ],
        recommended_articles=[
            RecommendedArticle(**a) for a in content.get("recommended_articles", [])
        ],
        skill_gaps=content.get("skill_gaps", []),
        generated_at=created_at,
        model_used=cache.model_used,
    )
