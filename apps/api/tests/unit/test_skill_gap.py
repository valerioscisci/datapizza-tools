"""Tests for AI Skill Gap Analysis route handlers.

Covers:
- POST /ai/skill-gap-analysis (with skills, no skills, AI unavailable, AI error)
- GET /ai/skill-gap-analysis (cached, not cached/404)
- GET /ai/market-trends (fresh, cached)
- Helper functions (_compute_skill_demand, _classify_demand, _find_matching_courses)
- Edge cases: no jobs, all skills in demand, company user, unauthenticated
GeminiAdvisor is always mocked — no real API calls.
"""

from __future__ import annotations

import importlib
import json
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import HTTPException

# Import the actual router module using importlib (learning #23)
_router_module = importlib.import_module("api.routes.ai.router")

generate_skill_gap_analysis = _router_module.generate_skill_gap_analysis
get_cached_skill_gap_analysis = _router_module.get_cached_skill_gap_analysis
get_market_trends = _router_module.get_market_trends
_compute_skill_demand = _router_module._compute_skill_demand
_classify_demand = _router_module._classify_demand
_find_matching_courses = _router_module._find_matching_courses
_get_valid_cache = _router_module._get_valid_cache


# --- Helper factories ---


def _make_job(job_id=None, title="Python Developer", company="TechCorp", location="Milano",
              work_mode="hybrid", tags_json='["Python"]', experience_level="mid",
              description="A great job", created_at=None):
    """Create a mock Job with all fields set."""
    job = MagicMock()
    job.id = job_id or str(uuid4())
    job.title = title
    job.company = company
    job.location = location
    job.work_mode = work_mode
    job.tags_json = tags_json
    job.experience_level = experience_level
    job.description = description
    job.is_active = 1
    job.created_at = created_at or datetime(2024, 6, 1, tzinfo=timezone.utc)
    return job


def _make_course(course_id=None, title="ML Course", provider="Coursera",
                 level="intermediate", category="ML", tags_json='["Python", "Machine Learning"]'):
    """Create a mock Course."""
    course = MagicMock()
    course.id = course_id or str(uuid4())
    course.title = title
    course.provider = provider
    course.level = level
    course.category = category
    course.tags_json = tags_json
    course.is_active = 1
    return course


def _make_cache(user_id, cache_type, content, model_used="gemini-2.0-flash",
                expired=False, naive_datetime=False, ttl_hours=24):
    """Create a mock AICache entry."""
    cache = MagicMock()
    cache.id = str(uuid4())
    cache.user_id = user_id
    cache.cache_type = cache_type
    cache.content_json = json.dumps(content, ensure_ascii=False)
    cache.model_used = model_used

    now = datetime.now(timezone.utc)
    if naive_datetime:
        cache.created_at = now.replace(tzinfo=None)
        if expired:
            cache.expires_at = (now - timedelta(hours=1)).replace(tzinfo=None)
        else:
            cache.expires_at = (now + timedelta(hours=ttl_hours)).replace(tzinfo=None)
    else:
        cache.created_at = now
        if expired:
            cache.expires_at = now - timedelta(hours=1)
        else:
            cache.expires_at = now + timedelta(hours=ttl_hours)

    return cache


def _mock_advisor(is_available=True, skill_gap_result=None):
    """Create a mock GeminiAdvisor for skill gap tests."""
    advisor = MagicMock()
    advisor.is_available = is_available
    advisor._model = "gemini-2.0-flash"
    advisor.model_name = "gemini-2.0-flash"
    advisor.skill_gap_analysis.return_value = skill_gap_result
    return advisor


def _setup_db_for_skill_gap(mock_db, user_id, jobs=None, courses=None,
                             experiences=None, news_items=None):
    """Configure mock_db query chains for skill gap endpoints."""
    job_query = MagicMock()
    job_query.filter.return_value.all.return_value = jobs or []
    job_query.filter.return_value.limit.return_value.all.return_value = jobs or []

    course_query = MagicMock()
    course_query.filter.return_value.all.return_value = courses or []

    experience_query = MagicMock()
    experience_query.filter.return_value.order_by.return_value.all.return_value = experiences or []

    news_query = MagicMock()
    news_query.filter.return_value.order_by.return_value.limit.return_value.all.return_value = news_items or []

    cache_query = MagicMock()
    cache_query.filter.return_value.order_by.return_value.first.return_value = None
    cache_query.filter.return_value.delete.return_value = 0

    def query_side_effect(model):
        from api.database.models import (
            Experience as ExpModel, Job as JobModel,
            Course as CourseModel, News as NewsModel, AICache as AICacheModel
        )
        if model is ExpModel:
            return experience_query
        elif model is JobModel:
            return job_query
        elif model is CourseModel:
            return course_query
        elif model is NewsModel:
            return news_query
        elif model is AICacheModel:
            return cache_query
        return MagicMock()

    mock_db.query.side_effect = query_side_effect
    return mock_db


# --- Helper function tests ---


class TestComputeSkillDemand:
    """Tests for the _compute_skill_demand helper."""

    def test_counts_skills_across_jobs(self, mock_db):
        """Should count skill occurrences across all active jobs."""
        jobs = [
            _make_job(tags_json='["Python", "FastAPI"]'),
            _make_job(tags_json='["Python", "Docker"]'),
            _make_job(tags_json='["React", "TypeScript"]'),
        ]
        mock_db.query.return_value.filter.return_value.all.return_value = jobs

        result = _compute_skill_demand(mock_db)

        assert result["skill_counts"]["Python"] == 2
        assert result["skill_counts"]["FastAPI"] == 1
        assert result["skill_counts"]["Docker"] == 1
        assert result["skill_counts"]["React"] == 1
        assert result["total_jobs"] == 3

    def test_empty_jobs(self, mock_db):
        """Should handle no active jobs gracefully."""
        mock_db.query.return_value.filter.return_value.all.return_value = []

        result = _compute_skill_demand(mock_db)

        assert result["skill_counts"] == {}
        assert result["skill_trends"] == {}
        assert result["total_jobs"] == 0

    def test_trend_direction_up(self, mock_db):
        """Should detect upward trend for skills with recent growth."""
        now = datetime.now(timezone.utc)
        # 3 recent jobs (last 15 days) with Python, 0 previous
        recent_jobs = [
            _make_job(tags_json='["Python"]', created_at=now - timedelta(days=5)),
            _make_job(tags_json='["Python"]', created_at=now - timedelta(days=10)),
            _make_job(tags_json='["Python"]', created_at=now - timedelta(days=3)),
        ]
        mock_db.query.return_value.filter.return_value.all.return_value = recent_jobs

        result = _compute_skill_demand(mock_db)

        assert result["skill_trends"]["Python"]["direction"] == "up"
        assert result["skill_trends"]["Python"]["pct"] > 10.0

    def test_trend_direction_down(self, mock_db):
        """Should detect downward trend for skills declining in recent period."""
        now = datetime.now(timezone.utc)
        # 0 recent, 3 previous (16-30 days ago) with Java
        previous_jobs = [
            _make_job(tags_json='["Java"]', created_at=now - timedelta(days=20)),
            _make_job(tags_json='["Java"]', created_at=now - timedelta(days=25)),
            _make_job(tags_json='["Java"]', created_at=now - timedelta(days=28)),
        ]
        mock_db.query.return_value.filter.return_value.all.return_value = previous_jobs

        result = _compute_skill_demand(mock_db)

        assert result["skill_trends"]["Java"]["direction"] == "down"
        assert result["skill_trends"]["Java"]["pct"] < -10.0

    def test_handles_naive_datetime_in_jobs(self, mock_db):
        """Should handle naive datetimes from SQLite in job created_at."""
        now = datetime.now(timezone.utc)
        job = _make_job(tags_json='["Go"]', created_at=(now - timedelta(days=5)).replace(tzinfo=None))
        mock_db.query.return_value.filter.return_value.all.return_value = [job]

        result = _compute_skill_demand(mock_db)

        assert result["skill_counts"]["Go"] == 1
        assert "Go" in result["skill_trends"]

    def test_normalizes_skill_tags(self, mock_db):
        """Should strip whitespace from skill tags."""
        job = _make_job(tags_json='["  Python  ", " React "]')
        mock_db.query.return_value.filter.return_value.all.return_value = [job]

        result = _compute_skill_demand(mock_db)

        assert "Python" in result["skill_counts"]
        assert "React" in result["skill_counts"]


class TestClassifyDemand:
    """Tests for the _classify_demand helper."""

    def test_green_when_high_demand_stable(self):
        """Should classify as green when ratio >= 20% and trend is not down."""
        # 3 out of 10 = 30% >= 20%
        assert _classify_demand(3, 10, "stable") == "green"

    def test_green_when_high_demand_up(self):
        """Should classify as green when ratio >= 20% and trend is up."""
        assert _classify_demand(2, 10, "up") == "green"

    def test_yellow_when_medium_demand(self):
        """Should classify as yellow when ratio between 5% and 20%."""
        # 1 out of 10 = 10%, between 5% and 20%
        assert _classify_demand(1, 10, "stable") == "yellow"

    def test_red_when_low_demand(self):
        """Should classify as red when ratio < 5%."""
        # 0 out of 10 = 0%
        assert _classify_demand(0, 10, "stable") == "red"

    def test_red_when_low_and_down(self):
        """Should classify as red when ratio < 5% and trend is down."""
        assert _classify_demand(0, 10, "down") == "red"

    def test_yellow_when_high_demand_but_down(self):
        """Should not classify as green when trend is down, even with high ratio."""
        # 3 out of 10 = 30% >= 20%, but trend is down
        assert _classify_demand(3, 10, "down") == "yellow"

    def test_yellow_when_zero_jobs(self):
        """Should classify as yellow when total_jobs is 0."""
        assert _classify_demand(0, 0, "stable") == "yellow"


class TestFindMatchingCourses:
    """Tests for the _find_matching_courses helper."""

    def test_matches_by_tag(self):
        """Should find courses matching skill in tags."""
        courses = [
            _make_course(course_id="c1", tags_json='["Python", "Django"]'),
            _make_course(course_id="c2", tags_json='["JavaScript", "React"]'),
        ]
        result = _find_matching_courses("Python", courses)
        assert "c1" in result
        assert "c2" not in result

    def test_matches_by_title(self):
        """Should find courses matching skill in title."""
        courses = [
            _make_course(course_id="c1", title="Advanced Python Programming", tags_json='["Django"]'),
        ]
        result = _find_matching_courses("python", courses)
        assert "c1" in result

    def test_case_insensitive_match(self):
        """Should match case-insensitively."""
        courses = [
            _make_course(course_id="c1", tags_json='["PYTHON"]'),
        ]
        result = _find_matching_courses("python", courses)
        assert "c1" in result

    def test_caps_at_three_courses(self):
        """Should return at most 3 matching courses."""
        courses = [
            _make_course(course_id=f"c{i}", tags_json='["Python"]') for i in range(5)
        ]
        result = _find_matching_courses("Python", courses)
        assert len(result) == 3

    def test_no_matches(self):
        """Should return empty list when no courses match."""
        courses = [
            _make_course(course_id="c1", tags_json='["Java"]', title="Java Course"),
        ]
        result = _find_matching_courses("Rust", courses)
        assert result == []

    def test_empty_courses_list(self):
        """Should handle empty courses list."""
        result = _find_matching_courses("Python", [])
        assert result == []


# --- POST /ai/skill-gap-analysis ---


class TestGenerateSkillGapAnalysis:
    """Tests for the POST /ai/skill-gap-analysis endpoint."""

    @pytest.mark.asyncio
    async def test_generates_analysis_with_skills(self, mock_db, mock_user):
        """Should generate skill gap analysis with algorithmic + AI data."""
        jobs = [
            _make_job(tags_json='["Python", "FastAPI", "Docker"]'),
            _make_job(tags_json='["Python", "React"]'),
        ]
        courses = [_make_course(course_id="c1", tags_json='["Docker"]')]

        ai_result = {
            "personalized_insights": "Sei ben posizionato nel mercato.",
            "missing_skill_reasons": {"Docker": "Docker e' essenziale per il deploy moderno."},
        }
        advisor = _mock_advisor(skill_gap_result=ai_result)

        _setup_db_for_skill_gap(mock_db, mock_user.id, jobs=jobs, courses=courses)

        with patch.object(_router_module, "get_advisor", return_value=advisor):
            result = await generate_skill_gap_analysis(current_user=mock_user, db=mock_db)

        assert len(result.user_skills) == 2  # Python, FastAPI
        assert result.personalized_insights == "Sei ben posizionato nel mercato."
        assert not result.no_skills_warning
        assert not result.ai_unavailable
        assert result.model_used == "gemini-2.0-flash"

    @pytest.mark.asyncio
    async def test_no_skills_warning(self, mock_db, mock_user):
        """Should set no_skills_warning when user has no skills."""
        mock_user.skills_json = "[]"
        jobs = [_make_job(tags_json='["Python"]')]
        advisor = _mock_advisor()

        _setup_db_for_skill_gap(mock_db, mock_user.id, jobs=jobs)

        with patch.object(_router_module, "get_advisor", return_value=advisor):
            result = await generate_skill_gap_analysis(current_user=mock_user, db=mock_db)

        assert result.no_skills_warning is True
        assert result.user_skills == []
        assert len(result.missing_skills) > 0
        # AI should NOT be called when no skills
        advisor.skill_gap_analysis.assert_not_called()

    @pytest.mark.asyncio
    async def test_ai_unavailable_graceful_degradation(self, mock_db, mock_user):
        """Should return algorithmic data with ai_unavailable=True when AI is down."""
        jobs = [_make_job(tags_json='["Python", "Docker"]')]
        advisor = _mock_advisor(is_available=False)

        _setup_db_for_skill_gap(mock_db, mock_user.id, jobs=jobs)

        with patch.object(_router_module, "get_advisor", return_value=advisor):
            result = await generate_skill_gap_analysis(current_user=mock_user, db=mock_db)

        assert result.ai_unavailable is True
        assert result.personalized_insights is None
        # Algorithmic data should still be present
        assert len(result.user_skills) > 0

    @pytest.mark.asyncio
    async def test_ai_returns_none_graceful_degradation(self, mock_db, mock_user):
        """Should handle AI returning None (error) gracefully."""
        jobs = [_make_job(tags_json='["Python"]')]
        advisor = _mock_advisor(skill_gap_result=None)

        _setup_db_for_skill_gap(mock_db, mock_user.id, jobs=jobs)

        with patch.object(_router_module, "get_advisor", return_value=advisor):
            result = await generate_skill_gap_analysis(current_user=mock_user, db=mock_db)

        assert result.ai_unavailable is True
        assert result.personalized_insights is None
        # Algorithmic data still present
        assert len(result.user_skills) > 0

    @pytest.mark.asyncio
    async def test_no_jobs_returns_empty_data(self, mock_db, mock_user):
        """Should handle case with no active jobs."""
        advisor = _mock_advisor(is_available=False)

        _setup_db_for_skill_gap(mock_db, mock_user.id, jobs=[])

        with patch.object(_router_module, "get_advisor", return_value=advisor):
            result = await generate_skill_gap_analysis(current_user=mock_user, db=mock_db)

        # User skills should still be listed but with 0 job counts
        for s in result.user_skills:
            assert s.job_count == 0
        assert result.missing_skills == []
        assert result.market_trends == []

    @pytest.mark.asyncio
    async def test_enriches_missing_skills_with_ai_reasons(self, mock_db, mock_user):
        """Should enrich missing skills with AI-generated reasons."""
        jobs = [_make_job(tags_json='["Python", "Docker", "Kubernetes"]')]
        ai_result = {
            "personalized_insights": "Dovresti imparare Docker.",
            "missing_skill_reasons": {
                "Docker": "Docker e' fondamentale per il deploy.",
                "Kubernetes": "K8s completa le competenze DevOps.",
            },
        }
        advisor = _mock_advisor(skill_gap_result=ai_result)

        _setup_db_for_skill_gap(mock_db, mock_user.id, jobs=jobs)

        with patch.object(_router_module, "get_advisor", return_value=advisor):
            result = await generate_skill_gap_analysis(current_user=mock_user, db=mock_db)

        docker_skill = next((m for m in result.missing_skills if m.skill == "Docker"), None)
        assert docker_skill is not None
        assert docker_skill.reason == "Docker e' fondamentale per il deploy."

    @pytest.mark.asyncio
    async def test_company_user_can_generate(self, mock_db, mock_company_user):
        """Should work for company users too (they have empty skills)."""
        mock_company_user.skills_json = "[]"
        jobs = [_make_job(tags_json='["Python"]')]
        advisor = _mock_advisor(is_available=False)

        _setup_db_for_skill_gap(mock_db, mock_company_user.id, jobs=jobs)

        with patch.object(_router_module, "get_advisor", return_value=advisor):
            result = await generate_skill_gap_analysis(current_user=mock_company_user, db=mock_db)

        assert result.no_skills_warning is True


# --- GET /ai/skill-gap-analysis ---


class TestGetCachedSkillGapAnalysis:
    """Tests for the GET /ai/skill-gap-analysis endpoint."""

    @pytest.mark.asyncio
    async def test_returns_cached_analysis(self, mock_db, mock_user):
        """Should return cached skill gap analysis when valid cache exists."""
        content = {
            "user_skills": [{"skill": "Python", "demand_status": "green", "trend_direction": "up", "trend_percentage": 15.0, "job_count": 5}],
            "missing_skills": [{"skill": "Docker", "demand_level": "high", "job_count": 3, "recommended_courses": ["c1"], "reason": "Importante"}],
            "market_trends": [{"skill": "Python", "direction": "up", "change_percentage": 15.0, "job_count": 5}],
            "personalized_insights": "Analisi cached.",
            "no_skills_warning": False,
            "ai_unavailable": False,
        }
        cache = _make_cache(mock_user.id, "skill_gap_analysis", content)

        mock_db.query.return_value.filter.return_value.order_by.return_value.first.return_value = cache

        result = await get_cached_skill_gap_analysis(current_user=mock_user, db=mock_db)

        assert len(result.user_skills) == 1
        assert result.user_skills[0].skill == "Python"
        assert result.personalized_insights == "Analisi cached."
        assert result.model_used == "gemini-2.0-flash"

    @pytest.mark.asyncio
    async def test_raises_404_when_no_cache(self, mock_db, mock_user):
        """Should raise 404 when no cached analysis exists."""
        mock_db.query.return_value.filter.return_value.order_by.return_value.first.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            await get_cached_skill_gap_analysis(current_user=mock_user, db=mock_db)
        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_raises_404_when_cache_expired(self, mock_db, mock_user):
        """Should raise 404 when cached analysis is expired."""
        content = {"user_skills": [], "missing_skills": [], "market_trends": [], "personalized_insights": None, "no_skills_warning": False, "ai_unavailable": False}
        cache = _make_cache(mock_user.id, "skill_gap_analysis", content, expired=True)

        mock_db.query.return_value.filter.return_value.order_by.return_value.first.return_value = cache

        with pytest.raises(HTTPException) as exc_info:
            await get_cached_skill_gap_analysis(current_user=mock_user, db=mock_db)
        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_handles_naive_datetime_in_cache(self, mock_db, mock_user):
        """Should handle naive datetimes from SQLite cache."""
        content = {"user_skills": [], "missing_skills": [], "market_trends": [], "personalized_insights": None, "no_skills_warning": True, "ai_unavailable": True}
        cache = _make_cache(mock_user.id, "skill_gap_analysis", content, naive_datetime=True)

        mock_db.query.return_value.filter.return_value.order_by.return_value.first.return_value = cache

        result = await get_cached_skill_gap_analysis(current_user=mock_user, db=mock_db)
        assert result.no_skills_warning is True


# --- GET /ai/market-trends ---


class TestGetMarketTrends:
    """Tests for the GET /ai/market-trends endpoint."""

    @pytest.mark.asyncio
    async def test_returns_cached_trends(self, mock_db, mock_user):
        """Should return cached market trends when valid cache exists."""
        content = {
            "trends": [
                {"skill": "Python", "direction": "up", "change_percentage": 20.0, "job_count": 8},
                {"skill": "React", "direction": "stable", "change_percentage": 0.0, "job_count": 5},
            ],
            "total_active_jobs": 10,
        }
        cache = _make_cache("__global__", "market_trends", content, ttl_hours=1)

        mock_db.query.return_value.filter.return_value.order_by.return_value.first.return_value = cache

        result = await get_market_trends(current_user=mock_user, db=mock_db)

        assert len(result.trends) == 2
        assert result.trends[0].skill == "Python"
        assert result.total_active_jobs == 10

    @pytest.mark.asyncio
    async def test_computes_fresh_trends_when_no_cache(self, mock_db, mock_user):
        """Should compute fresh trends when no cache exists."""
        jobs = [
            _make_job(tags_json='["Python", "Docker"]'),
            _make_job(tags_json='["Python", "React"]'),
            _make_job(tags_json='["Go"]'),
        ]

        # First call: _get_valid_cache returns None (no cache)
        cache_query = MagicMock()
        cache_query.filter.return_value.order_by.return_value.first.return_value = None
        cache_query.filter.return_value.delete.return_value = 0

        job_query = MagicMock()
        job_query.filter.return_value.all.return_value = jobs

        def query_side_effect(model):
            from api.database.models import Job as JobModel, AICache as AICacheModel
            if model is JobModel:
                return job_query
            elif model is AICacheModel:
                return cache_query
            return MagicMock()

        mock_db.query.side_effect = query_side_effect

        result = await get_market_trends(current_user=mock_user, db=mock_db)

        assert result.total_active_jobs == 3
        assert len(result.trends) > 0
        # Python should be the top skill (appears in 2 jobs)
        skill_names = [t.skill for t in result.trends]
        assert "Python" in skill_names

    @pytest.mark.asyncio
    async def test_caches_with_1h_ttl(self, mock_db, mock_user):
        """Should save computed trends to cache with 1h TTL."""
        jobs = [_make_job(tags_json='["Python"]')]

        cache_query = MagicMock()
        cache_query.filter.return_value.order_by.return_value.first.return_value = None
        cache_query.filter.return_value.delete.return_value = 0

        job_query = MagicMock()
        job_query.filter.return_value.all.return_value = jobs

        def query_side_effect(model):
            from api.database.models import Job as JobModel, AICache as AICacheModel
            if model is JobModel:
                return job_query
            elif model is AICacheModel:
                return cache_query
            return MagicMock()

        mock_db.query.side_effect = query_side_effect

        result = await get_market_trends(current_user=mock_user, db=mock_db)

        # Verify db.add was called with an AICache entry
        mock_db.add.assert_called_once()
        added_cache = mock_db.add.call_args[0][0]
        assert added_cache.user_id == "__global__"
        assert added_cache.cache_type == "market_trends"
        # Verify the TTL is ~1 hour
        delta = added_cache.expires_at - added_cache.created_at
        assert abs(delta.total_seconds() - 3600) < 5  # Within 5 seconds of 1 hour

    @pytest.mark.asyncio
    async def test_handles_no_jobs(self, mock_db, mock_user):
        """Should handle case with no active jobs."""
        cache_query = MagicMock()
        cache_query.filter.return_value.order_by.return_value.first.return_value = None
        cache_query.filter.return_value.delete.return_value = 0

        job_query = MagicMock()
        job_query.filter.return_value.all.return_value = []

        def query_side_effect(model):
            from api.database.models import Job as JobModel, AICache as AICacheModel
            if model is JobModel:
                return job_query
            elif model is AICacheModel:
                return cache_query
            return MagicMock()

        mock_db.query.side_effect = query_side_effect

        result = await get_market_trends(current_user=mock_user, db=mock_db)

        assert result.total_active_jobs == 0
        assert result.trends == []


# --- Schema tests ---


class TestSkillGapSchemas:
    """Tests for the Skill Gap Pydantic schemas."""

    def test_skill_demand_status_valid(self):
        """Should create a valid SkillDemandStatus."""
        from api.routes.ai.schemas import SkillDemandStatus
        s = SkillDemandStatus(skill="Python", demand_status="green", trend_direction="up", trend_percentage=15.0, job_count=5)
        assert s.skill == "Python"
        assert s.demand_status == "green"

    def test_missing_skill_valid(self):
        """Should create a valid MissingSkill with defaults."""
        from api.routes.ai.schemas import MissingSkill
        m = MissingSkill(skill="Docker", demand_level="high", job_count=3)
        assert m.recommended_courses == []
        assert m.reason == ""

    def test_market_trend_valid(self):
        """Should create a valid MarketTrend."""
        from api.routes.ai.schemas import MarketTrend
        t = MarketTrend(skill="React", direction="stable", change_percentage=0.0, job_count=4)
        assert t.direction == "stable"

    def test_skill_gap_analysis_response_valid(self):
        """Should create a valid SkillGapAnalysisResponse with all fields."""
        from api.routes.ai.schemas import SkillGapAnalysisResponse
        now = datetime.now(timezone.utc)
        resp = SkillGapAnalysisResponse(
            user_skills=[],
            missing_skills=[],
            market_trends=[],
            personalized_insights=None,
            no_skills_warning=True,
            ai_unavailable=True,
            generated_at=now,
        )
        assert resp.no_skills_warning is True
        assert resp.model_used is None

    def test_market_trends_response_valid(self):
        """Should create a valid MarketTrendsResponse."""
        from api.routes.ai.schemas import MarketTrendsResponse
        now = datetime.now(timezone.utc)
        resp = MarketTrendsResponse(
            trends=[],
            total_active_jobs=10,
            generated_at=now,
        )
        assert resp.total_active_jobs == 10

    def test_skill_gap_response_defaults(self):
        """Should use correct defaults for optional fields."""
        from api.routes.ai.schemas import SkillGapAnalysisResponse
        now = datetime.now(timezone.utc)
        resp = SkillGapAnalysisResponse(generated_at=now)
        assert resp.user_skills == []
        assert resp.missing_skills == []
        assert resp.market_trends == []
        assert resp.personalized_insights is None
        assert resp.no_skills_warning is False
        assert resp.ai_unavailable is False
        assert resp.model_used is None


# --- GeminiAdvisor skill_gap_analysis method tests ---


class TestGeminiAdvisorSkillGap:
    """Tests for the GeminiAdvisor.skill_gap_analysis method."""

    def test_returns_none_when_unavailable(self):
        """Should return None when advisor is not available."""
        from api.services.ai_advisor import GeminiAdvisor
        advisor = GeminiAdvisor.__new__(GeminiAdvisor)
        advisor._initialized = True
        advisor._api_key = None
        advisor._client = None
        advisor._model = "test"

        result = advisor.skill_gap_analysis(
            user_profile_dict={"skills": []},
            user_skills_status=[],
            missing_skills_data=[],
            market_trends_data=[],
            news_list=[],
        )
        assert result is None
