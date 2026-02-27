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
    SkillGapAnalysisResponse,
    SkillDemandStatus,
    MissingSkill,
    MarketTrend,
    MarketTrendsResponse,
)
from api.auth import get_current_user
from api.services.ai_advisor import get_advisor
from api.utils import safe_parse_json_list

logger = structlog.get_logger()

router = APIRouter(prefix="/ai", tags=["AI"])

CACHE_TTL_HOURS = 24

# --- Constants for skill gap demand classification ---
DEMAND_GREEN_THRESHOLD = 0.20   # >= 20% of jobs
DEMAND_YELLOW_THRESHOLD = 0.05  # >= 5% of jobs
TREND_UP_THRESHOLD = 10.0       # > 10% increase
TREND_DOWN_THRESHOLD = -10.0    # < -10% decrease
MARKET_TRENDS_CACHE_TTL_HOURS = 1


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


@router.post(
    "/job-matches",
    response_model=JobMatchResponse,
    summary="Generate AI job match scores",
    responses={
        401: {"description": "Not authenticated"},
        503: {"description": "AI service unavailable or failed to generate matches"},
    },
)
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


@router.get(
    "/job-matches",
    response_model=JobMatchResponse,
    summary="Get cached AI job matches",
    responses={
        401: {"description": "Not authenticated"},
        404: {"description": "No cached job matches found — generate new matches first"},
    },
)
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


@router.post(
    "/career-advice",
    response_model=CareerAdviceResponse,
    summary="Generate AI career recommendations",
    responses={
        401: {"description": "Not authenticated"},
        503: {"description": "AI service unavailable or failed to generate career advice"},
    },
)
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


@router.get(
    "/career-advice",
    response_model=CareerAdviceResponse,
    summary="Get cached AI career advice",
    responses={
        401: {"description": "Not authenticated"},
        404: {"description": "No cached career advice found — generate new advice first"},
    },
)
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


# --- Skill Gap Analysis helpers ---


def _compute_skill_demand(db: Session) -> dict:
    """Compute skill demand from all active jobs.

    Returns:
        {
            "skill_counts": {"Python": 5, "React": 3, ...},
            "skill_trends": {"Python": {"recent": 3, "previous": 2, "pct": 50.0, "direction": "up"}, ...},
            "total_jobs": 10,
        }
    """
    now = datetime.now(timezone.utc)
    cutoff_recent = now - timedelta(days=15)
    cutoff_previous = now - timedelta(days=30)

    all_active_jobs = db.query(Job).filter(Job.is_active == 1).all()
    total_jobs = len(all_active_jobs)

    # Count skill occurrences across all jobs
    skill_counts: dict[str, int] = {}
    recent_counts: dict[str, int] = {}
    previous_counts: dict[str, int] = {}

    for job in all_active_jobs:
        tags = safe_parse_json_list(job.tags_json)
        created_at = job.created_at
        if created_at and created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)

        for tag in tags:
            tag_normalized = tag.strip()
            skill_counts[tag_normalized] = skill_counts.get(tag_normalized, 0) + 1

            if created_at and created_at >= cutoff_recent:
                recent_counts[tag_normalized] = recent_counts.get(tag_normalized, 0) + 1
            elif created_at and created_at >= cutoff_previous:
                previous_counts[tag_normalized] = previous_counts.get(tag_normalized, 0) + 1

    # Compute trends
    all_skills = set(skill_counts.keys())
    skill_trends = {}
    for skill in all_skills:
        recent = recent_counts.get(skill, 0)
        previous = previous_counts.get(skill, 0)
        pct = ((recent - previous) / max(previous, 1)) * 100
        if pct > TREND_UP_THRESHOLD:
            direction = "up"
        elif pct < TREND_DOWN_THRESHOLD:
            direction = "down"
        else:
            direction = "stable"
        skill_trends[skill] = {
            "recent": recent, "previous": previous,
            "pct": round(pct, 1), "direction": direction,
        }

    return {
        "skill_counts": skill_counts,
        "skill_trends": skill_trends,
        "total_jobs": total_jobs,
    }


def _classify_demand(count: int, total_jobs: int, trend_direction: str) -> str:
    """Classify a skill into green/yellow/red based on demand thresholds."""
    if total_jobs == 0:
        return "yellow"
    ratio = count / total_jobs
    if ratio >= DEMAND_GREEN_THRESHOLD and trend_direction != "down":
        return "green"
    elif ratio < DEMAND_YELLOW_THRESHOLD:
        return "red"
    else:
        return "yellow"


def _find_matching_courses(skill: str, courses: list[Course]) -> list[str]:
    """Find course IDs whose tags or title match a given skill (case-insensitive).

    Accepts a pre-fetched courses list to avoid querying the DB for each skill.
    """
    matching_ids = []
    skill_lower = skill.lower()
    for course in courses:
        tags = safe_parse_json_list(course.tags_json)
        tags_lower = [t.lower() for t in tags]
        if skill_lower in tags_lower or skill_lower in course.title.lower():
            matching_ids.append(course.id)
    return matching_ids[:3]  # Cap at 3 courses per skill


# --- POST /ai/skill-gap-analysis ---


@router.post(
    "/skill-gap-analysis",
    response_model=SkillGapAnalysisResponse,
    summary="Generate AI skill gap analysis",
    responses={
        401: {"description": "Not authenticated"},
    },
)
async def generate_skill_gap_analysis(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Generate skill gap analysis for the current user.

    Returns algorithmic demand data even if AI is unavailable.
    """
    user_skills = safe_parse_json_list(current_user.skills_json)
    no_skills_warning = len(user_skills) == 0

    # Step 1: Compute market demand (algorithmic)
    demand_data = _compute_skill_demand(db)
    skill_counts = demand_data["skill_counts"]
    skill_trends = demand_data["skill_trends"]
    total_jobs = demand_data["total_jobs"]

    # Step 2: Classify user skills (case-insensitive matching)
    skill_counts_lower = {k.lower(): v for k, v in skill_counts.items()}
    skill_trends_lower = {k.lower(): v for k, v in skill_trends.items()}
    user_skills_status = []
    for skill in user_skills:
        count = skill_counts_lower.get(skill.lower(), 0)
        trend_info = skill_trends_lower.get(skill.lower(), {"pct": 0.0, "direction": "stable"})
        demand_status = _classify_demand(count, total_jobs, trend_info["direction"])
        user_skills_status.append(SkillDemandStatus(
            skill=skill,
            demand_status=demand_status,
            trend_direction=trend_info["direction"],
            trend_percentage=trend_info["pct"],
            job_count=count,
        ))

    # Step 3: Find missing skills (in demand but not in user profile)
    # Pre-fetch all active courses once for efficiency
    all_courses = db.query(Course).filter(Course.is_active == 1).all()
    user_skills_lower = {s.lower() for s in user_skills}
    missing_skills = []
    sorted_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)
    for skill_name, count in sorted_skills:
        if skill_name.lower() not in user_skills_lower:
            trend_info = skill_trends.get(skill_name, {"pct": 0.0, "direction": "stable"})
            demand_level = "high" if count / max(total_jobs, 1) >= DEMAND_GREEN_THRESHOLD else (
                "medium" if count / max(total_jobs, 1) >= DEMAND_YELLOW_THRESHOLD else "low"
            )
            course_ids = _find_matching_courses(skill_name, all_courses)
            missing_skills.append(MissingSkill(
                skill=skill_name,
                demand_level=demand_level,
                job_count=count,
                recommended_courses=course_ids,
                reason="",  # Will be filled by AI if available
            ))
        if len(missing_skills) >= 10:
            break

    # Step 4: Build market trends list (top 15 skills by count)
    market_trends = []
    for skill_name, count in sorted_skills[:15]:
        trend_info = skill_trends.get(skill_name, {"pct": 0.0, "direction": "stable"})
        market_trends.append(MarketTrend(
            skill=skill_name,
            direction=trend_info["direction"],
            change_percentage=trend_info["pct"],
            job_count=count,
        ))

    # Step 5: Get AI personalized insights (optional, graceful degradation)
    advisor = get_advisor()
    personalized_insights = None
    ai_unavailable = False
    model_used = None

    if advisor.is_available and not no_skills_warning:
        # Fetch experiences and recent news for context
        experiences = (
            db.query(Experience)
            .filter(Experience.user_id == current_user.id)
            .order_by(Experience.start_year.desc())
            .all()
        )
        profile_dict = _build_user_profile_dict(current_user, experiences)

        news_items = (
            db.query(News)
            .filter(News.is_active == 1)
            .order_by(News.published_at.desc())
            .limit(10)
            .all()
        )
        news_list = _build_news_list(news_items)

        # Build context for Gemini
        ai_result = advisor.skill_gap_analysis(
            user_profile_dict=profile_dict,
            user_skills_status=[s.model_dump() for s in user_skills_status],
            missing_skills_data=[m.model_dump() for m in missing_skills],
            market_trends_data=[t.model_dump() for t in market_trends],
            news_list=news_list,
        )

        if ai_result is not None:
            personalized_insights = ai_result.get("personalized_insights", "")
            # Enrich missing skills with AI reasons
            ai_missing_reasons = ai_result.get("missing_skill_reasons", {})
            for ms in missing_skills:
                if ms.skill in ai_missing_reasons:
                    ms.reason = ai_missing_reasons[ms.skill]
            model_used = advisor.model_name
        else:
            ai_unavailable = True
    elif not advisor.is_available:
        ai_unavailable = True

    now = datetime.now(timezone.utc)

    # Step 6: Cache result
    cache_content = {
        "user_skills": [s.model_dump() for s in user_skills_status],
        "missing_skills": [m.model_dump() for m in missing_skills],
        "market_trends": [t.model_dump() for t in market_trends],
        "personalized_insights": personalized_insights,
        "no_skills_warning": no_skills_warning,
        "ai_unavailable": ai_unavailable,
    }
    cache = _save_cache(db, current_user.id, "skill_gap_analysis", cache_content, model_used)

    created_at = cache.created_at
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)

    return SkillGapAnalysisResponse(
        user_skills=user_skills_status,
        missing_skills=missing_skills,
        market_trends=market_trends,
        personalized_insights=personalized_insights,
        no_skills_warning=no_skills_warning,
        ai_unavailable=ai_unavailable,
        generated_at=created_at,
        model_used=model_used,
    )


# --- GET /ai/skill-gap-analysis ---


@router.get(
    "/skill-gap-analysis",
    response_model=SkillGapAnalysisResponse,
    summary="Get cached skill gap analysis",
    responses={
        401: {"description": "Not authenticated"},
        404: {"description": "No cached analysis found"},
    },
)
async def get_cached_skill_gap_analysis(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get cached skill gap analysis for the current user."""
    cache = _get_valid_cache(db, current_user.id, "skill_gap_analysis")
    if cache is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No cached skill gap analysis found. Generate a new analysis first.",
        )

    content = json.loads(cache.content_json)
    created_at = cache.created_at
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)

    return SkillGapAnalysisResponse(
        user_skills=[SkillDemandStatus(**s) for s in content.get("user_skills", [])],
        missing_skills=[MissingSkill(**m) for m in content.get("missing_skills", [])],
        market_trends=[MarketTrend(**t) for t in content.get("market_trends", [])],
        personalized_insights=content.get("personalized_insights"),
        no_skills_warning=content.get("no_skills_warning", False),
        ai_unavailable=content.get("ai_unavailable", False),
        generated_at=created_at,
        model_used=cache.model_used,
    )


# --- GET /ai/market-trends ---


@router.get(
    "/market-trends",
    response_model=MarketTrendsResponse,
    summary="Get current market skill trends",
    responses={
        401: {"description": "Not authenticated"},
    },
)
async def get_market_trends(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get global market trends (cached for 1 hour)."""
    # Check global cache
    cache = _get_valid_cache(db, "__global__", "market_trends")
    if cache is not None:
        content = json.loads(cache.content_json)
        created_at = cache.created_at
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)
        return MarketTrendsResponse(
            trends=[MarketTrend(**t) for t in content.get("trends", [])],
            total_active_jobs=content.get("total_active_jobs", 0),
            generated_at=created_at,
        )

    # Compute fresh
    demand_data = _compute_skill_demand(db)
    skill_counts = demand_data["skill_counts"]
    skill_trends = demand_data["skill_trends"]
    total_jobs = demand_data["total_jobs"]

    sorted_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)
    trends = []
    for skill_name, count in sorted_skills:
        trend_info = skill_trends.get(skill_name, {"pct": 0.0, "direction": "stable"})
        trends.append(MarketTrend(
            skill=skill_name,
            direction=trend_info["direction"],
            change_percentage=trend_info["pct"],
            job_count=count,
        ))

    now = datetime.now(timezone.utc)

    # Save with 1h TTL (override the default)
    # Delete old global cache
    db.query(AICache).filter(
        AICache.user_id == "__global__", AICache.cache_type == "market_trends"
    ).delete()

    global_cache = AICache(
        id=str(uuid.uuid4()),
        user_id="__global__",
        cache_type="market_trends",
        content_json=json.dumps({
            "trends": [t.model_dump() for t in trends],
            "total_active_jobs": total_jobs,
        }, ensure_ascii=False, default=str),
        model_used=None,
        created_at=now,
        expires_at=now + timedelta(hours=MARKET_TRENDS_CACHE_TTL_HOURS),
    )
    db.add(global_cache)
    db.commit()
    db.refresh(global_cache)

    return MarketTrendsResponse(
        trends=trends,
        total_active_jobs=total_jobs,
        generated_at=now,
    )
