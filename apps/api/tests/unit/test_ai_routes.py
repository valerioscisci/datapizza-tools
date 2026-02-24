"""Tests for AI route handlers (api/routes/ai/).

Covers all 4 endpoints: POST/GET job-matches, POST/GET career-advice.
Tests auth required, cache hit/miss/expiry, Gemini unavailable,
malformed Gemini responses, empty profiles, and no active jobs.
GeminiAdvisor is always mocked — no real API calls.
"""

from __future__ import annotations

import importlib
import json
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch, patch as mock_patch
from uuid import uuid4

import pytest
from fastapi import HTTPException

# Import the actual router module using importlib (learning #23)
_router_module = importlib.import_module("api.routes.ai.router")

generate_job_matches = _router_module.generate_job_matches
get_cached_job_matches = _router_module.get_cached_job_matches
generate_career_advice = _router_module.generate_career_advice
get_cached_career_advice = _router_module.get_cached_career_advice
_build_user_profile_dict = _router_module._build_user_profile_dict
_build_jobs_list = _router_module._build_jobs_list
_build_courses_list = _router_module._build_courses_list
_build_news_list = _router_module._build_news_list
_get_valid_cache = _router_module._get_valid_cache
_save_cache = _router_module._save_cache


# --- Helper factories ---


def _make_job(job_id=None, title="Python Developer", company="TechCorp", location="Milano",
              work_mode="hybrid", tags_json='["Python"]', experience_level="mid",
              description="A great job"):
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
    job.created_at = datetime(2024, 6, 1, tzinfo=timezone.utc)
    return job


def _make_experience(user_id=None, title="Developer", company="StartupXYZ",
                     start_year=2020, end_year=None, is_current=1, description="Coding"):
    """Create a mock Experience."""
    exp = MagicMock()
    exp.id = str(uuid4())
    exp.user_id = user_id or str(uuid4())
    exp.title = title
    exp.company = company
    exp.start_year = start_year
    exp.end_year = end_year
    exp.is_current = is_current
    exp.description = description
    return exp


def _make_course_item(course_id=None, title="ML Course", provider="Coursera",
                      level="intermediate", category="ML"):
    """Create a mock Course."""
    course = MagicMock()
    course.id = course_id or str(uuid4())
    course.title = title
    course.provider = provider
    course.level = level
    course.category = category
    course.is_active = 1
    return course


def _make_news_item(news_id=None, title="AI Trends", category="AI", summary="News about AI"):
    """Create a mock News."""
    news = MagicMock()
    news.id = news_id or str(uuid4())
    news.title = title
    news.category = category
    news.summary = summary
    news.is_active = 1
    news.published_at = datetime(2024, 6, 15, tzinfo=timezone.utc)
    return news


def _make_cache(user_id, cache_type, content, model_used="gemini-2.0-flash",
                expired=False, naive_datetime=False):
    """Create a mock AICache entry."""
    cache = MagicMock()
    cache.id = str(uuid4())
    cache.user_id = user_id
    cache.cache_type = cache_type
    cache.content_json = json.dumps(content, ensure_ascii=False)
    cache.model_used = model_used

    now = datetime.now(timezone.utc)
    if naive_datetime:
        # SQLite stores naive datetimes (learning #26)
        cache.created_at = now.replace(tzinfo=None)
        if expired:
            cache.expires_at = (now - timedelta(hours=1)).replace(tzinfo=None)
        else:
            cache.expires_at = (now + timedelta(hours=24)).replace(tzinfo=None)
    else:
        cache.created_at = now
        if expired:
            cache.expires_at = now - timedelta(hours=1)
        else:
            cache.expires_at = now + timedelta(hours=24)

    return cache


def _mock_advisor(is_available=True, match_result=None, career_result=None):
    """Create a mock GeminiAdvisor."""
    advisor = MagicMock()
    advisor.is_available = is_available
    advisor._model = "gemini-2.0-flash"
    advisor.model_name = "gemini-2.0-flash"
    advisor.match_jobs.return_value = match_result
    advisor.career_recommendations.return_value = career_result
    return advisor


def _setup_db_for_generate(mock_db, user_id, jobs=None, experiences=None,
                           courses=None, news_items=None, existing_cache=None):
    """Configure the mock_db query chains for generate endpoints."""
    # We need to handle multiple query calls with different model types
    # Use side_effect to return different query chains based on the model
    experience_query = MagicMock()
    experience_query.filter.return_value.order_by.return_value.all.return_value = experiences or []

    job_query = MagicMock()
    job_query.filter.return_value.limit.return_value.all.return_value = jobs or []
    job_query.filter.return_value.all.return_value = jobs or []

    course_query = MagicMock()
    course_query.filter.return_value.all.return_value = courses or []

    news_query = MagicMock()
    news_query.filter.return_value.order_by.return_value.limit.return_value.all.return_value = news_items or []

    cache_query = MagicMock()
    cache_query.filter.return_value.order_by.return_value.first.return_value = existing_cache
    cache_query.filter.return_value.delete.return_value = 0

    # Also handle Job.id.in_() for top jobs lookup
    job_in_query = MagicMock()
    job_in_query.filter.return_value.all.return_value = jobs[:5] if jobs else []

    def query_side_effect(model):
        from api.database.models import Experience as ExpModel, Job as JobModel, Course as CourseModel, News as NewsModel, AICache as AICacheModel
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


# --- Helper tests ---


class TestBuildUserProfileDict:
    """Tests for the _build_user_profile_dict helper."""

    def test_builds_profile_with_skills_and_experiences(self, mock_user):
        """Should correctly extract skills, experience level and experience items."""
        exp = _make_experience(user_id=mock_user.id)
        result = _build_user_profile_dict(mock_user, [exp])

        assert result["skills"] == ["Python", "FastAPI"]
        assert result["experience_level"] == "mid"
        assert result["current_role"] == "Developer"
        assert result["location"] == "Milano"
        assert len(result["experiences"]) == 1
        assert result["experiences"][0]["title"] == "Developer"

    def test_builds_profile_empty_skills(self, mock_user):
        """Should return empty skills list for user with no skills."""
        mock_user.skills_json = "[]"
        result = _build_user_profile_dict(mock_user, [])

        assert result["skills"] == []
        assert result["experiences"] == []

    def test_builds_profile_null_skills(self, mock_user):
        """Should handle null skills_json gracefully."""
        mock_user.skills_json = None
        result = _build_user_profile_dict(mock_user, [])

        assert result["skills"] == []

    def test_experience_with_description(self, mock_user):
        """Should include description in experience when present."""
        exp = _make_experience(user_id=mock_user.id, description="Built APIs")
        result = _build_user_profile_dict(mock_user, [exp])

        assert result["experiences"][0]["description"] == "Built APIs"

    def test_experience_without_description(self, mock_user):
        """Should omit description key when experience has no description."""
        exp = _make_experience(user_id=mock_user.id, description=None)
        result = _build_user_profile_dict(mock_user, [exp])

        assert "description" not in result["experiences"][0]


class TestBuildJobsList:
    """Tests for the _build_jobs_list helper."""

    def test_builds_jobs_list(self):
        """Should build a list of job dicts with correct fields."""
        job = _make_job()
        result = _build_jobs_list([job])

        assert len(result) == 1
        assert result[0]["job_id"] == job.id
        assert result[0]["title"] == "Python Developer"
        assert result[0]["tags"] == ["Python"]

    def test_truncates_long_descriptions(self):
        """Should truncate descriptions to 300 chars."""
        job = _make_job(description="A" * 500)
        result = _build_jobs_list([job])

        assert len(result[0]["description"]) == 300

    def test_empty_list(self):
        """Should return empty list for empty input."""
        assert _build_jobs_list([]) == []


class TestBuildCoursesAndNewsList:
    """Tests for _build_courses_list and _build_news_list helpers."""

    def test_builds_courses_list(self):
        """Should build course dicts with correct fields."""
        course = _make_course_item()
        result = _build_courses_list([course])

        assert len(result) == 1
        assert result[0]["course_id"] == course.id
        assert result[0]["title"] == "ML Course"

    def test_builds_news_list(self):
        """Should build news dicts with correct fields."""
        news = _make_news_item()
        result = _build_news_list([news])

        assert len(result) == 1
        assert result[0]["news_id"] == news.id
        assert result[0]["title"] == "AI Trends"

    def test_truncates_long_news_summary(self):
        """Should truncate news summary to 200 chars."""
        news = _make_news_item(summary="B" * 400)
        result = _build_news_list([news])

        assert len(result[0]["summary"]) == 200


# --- Cache tests ---


class TestGetValidCache:
    """Tests for the _get_valid_cache helper."""

    def test_returns_valid_cache(self, mock_db, mock_user):
        """Should return cache when not expired."""
        cache = _make_cache(mock_user.id, "job_matches", [{"job_id": "1", "score": 80}])
        mock_db.query.return_value.filter.return_value.order_by.return_value.first.return_value = cache

        result = _get_valid_cache(mock_db, mock_user.id, "job_matches")
        assert result is not None

    def test_returns_none_for_expired_cache(self, mock_db, mock_user):
        """Should return None when cache is expired."""
        cache = _make_cache(mock_user.id, "job_matches", [], expired=True)
        mock_db.query.return_value.filter.return_value.order_by.return_value.first.return_value = cache

        result = _get_valid_cache(mock_db, mock_user.id, "job_matches")
        assert result is None

    def test_returns_none_when_no_cache(self, mock_db, mock_user):
        """Should return None when no cache entry exists."""
        mock_db.query.return_value.filter.return_value.order_by.return_value.first.return_value = None

        result = _get_valid_cache(mock_db, mock_user.id, "job_matches")
        assert result is None

    def test_handles_naive_datetime(self, mock_db, mock_user):
        """Should handle naive datetimes from SQLite (learning #26)."""
        cache = _make_cache(mock_user.id, "job_matches", [{"job_id": "1", "score": 80}], naive_datetime=True)
        mock_db.query.return_value.filter.return_value.order_by.return_value.first.return_value = cache

        result = _get_valid_cache(mock_db, mock_user.id, "job_matches")
        assert result is not None

    def test_handles_naive_expired_datetime(self, mock_db, mock_user):
        """Should correctly detect expired naive datetimes from SQLite."""
        cache = _make_cache(mock_user.id, "job_matches", [], expired=True, naive_datetime=True)
        mock_db.query.return_value.filter.return_value.order_by.return_value.first.return_value = cache

        result = _get_valid_cache(mock_db, mock_user.id, "job_matches")
        assert result is None


# --- POST /ai/job-matches ---


class TestGenerateJobMatches:
    """Tests for the POST /ai/job-matches endpoint."""

    @pytest.mark.asyncio
    async def test_generates_matches_successfully(self, mock_db, mock_user):
        """Should generate job matches and return them with cache."""
        job = _make_job()
        match_result = [{"job_id": job.id, "score": 85, "reasons": ["Good match"]}]
        advisor = _mock_advisor(match_result=match_result)

        _setup_db_for_generate(mock_db, mock_user.id, jobs=[job])

        with patch.object(_router_module, "get_advisor", return_value=advisor):
            result = await generate_job_matches(current_user=mock_user, db=mock_db)

        assert len(result.matches) == 1
        assert result.matches[0].job_id == job.id
        assert result.matches[0].score == 85
        assert result.matches[0].reasons == ["Good match"]
        assert result.model_used == "gemini-2.0-flash"

    @pytest.mark.asyncio
    async def test_raises_503_when_ai_unavailable(self, mock_db, mock_user):
        """Should raise 503 when Gemini is not available."""
        advisor = _mock_advisor(is_available=False)

        with patch.object(_router_module, "get_advisor", return_value=advisor):
            with pytest.raises(HTTPException) as exc_info:
                await generate_job_matches(current_user=mock_user, db=mock_db)
            assert exc_info.value.status_code == 503

    @pytest.mark.asyncio
    async def test_returns_empty_when_no_jobs(self, mock_db, mock_user):
        """Should return empty matches when no active jobs exist."""
        advisor = _mock_advisor()

        _setup_db_for_generate(mock_db, mock_user.id, jobs=[])

        with patch.object(_router_module, "get_advisor", return_value=advisor):
            result = await generate_job_matches(current_user=mock_user, db=mock_db)

        assert result.matches == []
        advisor.match_jobs.assert_not_called()

    @pytest.mark.asyncio
    async def test_raises_503_when_gemini_returns_none(self, mock_db, mock_user):
        """Should raise 503 when Gemini fails and returns None."""
        job = _make_job()
        advisor = _mock_advisor(match_result=None)

        _setup_db_for_generate(mock_db, mock_user.id, jobs=[job])

        with patch.object(_router_module, "get_advisor", return_value=advisor):
            with pytest.raises(HTTPException) as exc_info:
                await generate_job_matches(current_user=mock_user, db=mock_db)
            assert exc_info.value.status_code == 503

    @pytest.mark.asyncio
    async def test_clamps_score_to_0_100(self, mock_db, mock_user):
        """Should clamp score to [0, 100] range."""
        job = _make_job()
        match_result = [{"job_id": job.id, "score": 150, "reasons": ["Over 100"]}]
        advisor = _mock_advisor(match_result=match_result)

        _setup_db_for_generate(mock_db, mock_user.id, jobs=[job])

        with patch.object(_router_module, "get_advisor", return_value=advisor):
            result = await generate_job_matches(current_user=mock_user, db=mock_db)

        assert result.matches[0].score == 100

    @pytest.mark.asyncio
    async def test_clamps_negative_score_to_zero(self, mock_db, mock_user):
        """Should clamp negative score to 0."""
        job = _make_job()
        match_result = [{"job_id": job.id, "score": -10, "reasons": ["Negative"]}]
        advisor = _mock_advisor(match_result=match_result)

        _setup_db_for_generate(mock_db, mock_user.id, jobs=[job])

        with patch.object(_router_module, "get_advisor", return_value=advisor):
            result = await generate_job_matches(current_user=mock_user, db=mock_db)

        assert result.matches[0].score == 0

    @pytest.mark.asyncio
    async def test_with_user_experiences(self, mock_db, mock_user):
        """Should pass user experiences to advisor."""
        job = _make_job()
        exp = _make_experience(user_id=mock_user.id)
        match_result = [{"job_id": job.id, "score": 70, "reasons": ["OK"]}]
        advisor = _mock_advisor(match_result=match_result)

        _setup_db_for_generate(mock_db, mock_user.id, jobs=[job], experiences=[exp])

        with patch.object(_router_module, "get_advisor", return_value=advisor):
            result = await generate_job_matches(current_user=mock_user, db=mock_db)

        # Verify advisor was called with a profile that includes experiences
        call_args = advisor.match_jobs.call_args
        profile = call_args[0][0]
        assert len(profile["experiences"]) == 1

    @pytest.mark.asyncio
    async def test_empty_profile_user(self, mock_db, mock_user):
        """Should handle user with no skills and no experiences."""
        mock_user.skills_json = "[]"
        mock_user.experience_level = None
        mock_user.current_role = None

        job = _make_job()
        match_result = [{"job_id": job.id, "score": 20, "reasons": ["Low match"]}]
        advisor = _mock_advisor(match_result=match_result)

        _setup_db_for_generate(mock_db, mock_user.id, jobs=[job], experiences=[])

        with patch.object(_router_module, "get_advisor", return_value=advisor):
            result = await generate_job_matches(current_user=mock_user, db=mock_db)

        assert result.matches[0].score == 20

    @pytest.mark.asyncio
    async def test_multiple_jobs(self, mock_db, mock_user):
        """Should handle multiple job matches."""
        jobs = [_make_job(title=f"Job {i}") for i in range(3)]
        match_result = [
            {"job_id": jobs[0].id, "score": 90, "reasons": ["Best"]},
            {"job_id": jobs[1].id, "score": 60, "reasons": ["OK"]},
            {"job_id": jobs[2].id, "score": 30, "reasons": ["Low"]},
        ]
        advisor = _mock_advisor(match_result=match_result)

        _setup_db_for_generate(mock_db, mock_user.id, jobs=jobs)

        with patch.object(_router_module, "get_advisor", return_value=advisor):
            result = await generate_job_matches(current_user=mock_user, db=mock_db)

        assert len(result.matches) == 3
        scores = [m.score for m in result.matches]
        assert scores == [90, 60, 30]


# --- GET /ai/job-matches ---


class TestGetCachedJobMatches:
    """Tests for the GET /ai/job-matches endpoint."""

    @pytest.mark.asyncio
    async def test_returns_cached_matches(self, mock_db, mock_user):
        """Should return cached job matches when valid cache exists."""
        content = [{"job_id": "job-1", "score": 80, "reasons": ["Match"]}]
        cache = _make_cache(mock_user.id, "job_matches", content)

        mock_db.query.return_value.filter.return_value.order_by.return_value.first.return_value = cache

        result = await get_cached_job_matches(current_user=mock_user, db=mock_db)

        assert len(result.matches) == 1
        assert result.matches[0].job_id == "job-1"
        assert result.matches[0].score == 80

    @pytest.mark.asyncio
    async def test_raises_404_when_no_cache(self, mock_db, mock_user):
        """Should raise 404 when no cached matches exist."""
        mock_db.query.return_value.filter.return_value.order_by.return_value.first.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            await get_cached_job_matches(current_user=mock_user, db=mock_db)
        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_raises_404_when_cache_expired(self, mock_db, mock_user):
        """Should raise 404 when cache is expired."""
        content = [{"job_id": "job-1", "score": 80, "reasons": ["Match"]}]
        cache = _make_cache(mock_user.id, "job_matches", content, expired=True)

        mock_db.query.return_value.filter.return_value.order_by.return_value.first.return_value = cache

        with pytest.raises(HTTPException) as exc_info:
            await get_cached_job_matches(current_user=mock_user, db=mock_db)
        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_returns_model_used(self, mock_db, mock_user):
        """Should return the model_used from cache."""
        content = [{"job_id": "job-1", "score": 80, "reasons": ["Match"]}]
        cache = _make_cache(mock_user.id, "job_matches", content, model_used="gemini-2.0-flash")

        mock_db.query.return_value.filter.return_value.order_by.return_value.first.return_value = cache

        result = await get_cached_job_matches(current_user=mock_user, db=mock_db)
        assert result.model_used == "gemini-2.0-flash"

    @pytest.mark.asyncio
    async def test_handles_naive_datetime_in_cache(self, mock_db, mock_user):
        """Should handle naive datetimes from SQLite cache."""
        content = [{"job_id": "job-1", "score": 80, "reasons": ["Match"]}]
        cache = _make_cache(mock_user.id, "job_matches", content, naive_datetime=True)

        mock_db.query.return_value.filter.return_value.order_by.return_value.first.return_value = cache

        result = await get_cached_job_matches(current_user=mock_user, db=mock_db)
        assert len(result.matches) == 1

    @pytest.mark.asyncio
    async def test_clamps_cached_scores(self, mock_db, mock_user):
        """Should clamp scores from cached data."""
        content = [{"job_id": "job-1", "score": 200, "reasons": ["Over"]}]
        cache = _make_cache(mock_user.id, "job_matches", content)

        mock_db.query.return_value.filter.return_value.order_by.return_value.first.return_value = cache

        result = await get_cached_job_matches(current_user=mock_user, db=mock_db)
        assert result.matches[0].score == 100

    @pytest.mark.asyncio
    async def test_handles_missing_reasons_in_cache(self, mock_db, mock_user):
        """Should handle cached matches with missing reasons field."""
        content = [{"job_id": "job-1", "score": 80}]
        cache = _make_cache(mock_user.id, "job_matches", content)

        mock_db.query.return_value.filter.return_value.order_by.return_value.first.return_value = cache

        result = await get_cached_job_matches(current_user=mock_user, db=mock_db)
        assert result.matches[0].reasons == []


# --- POST /ai/career-advice ---


class TestGenerateCareerAdvice:
    """Tests for the POST /ai/career-advice endpoint."""

    @pytest.mark.asyncio
    async def test_generates_advice_successfully(self, mock_db, mock_user):
        """Should generate career advice and return it."""
        job = _make_job()
        course = _make_course_item()
        news = _make_news_item()

        career_result = {
            "career_direction": "Specializzati in AI/ML",
            "recommended_courses": [{"course_id": course.id, "reason": "Perfetto per le tue skill"}],
            "recommended_articles": [{"news_id": news.id, "reason": "Utile per il tuo settore"}],
            "skill_gaps": ["Docker", "Kubernetes"],
        }
        advisor = _mock_advisor(career_result=career_result)

        # Mock cache lookup for job_matches returns None (no existing cache)
        _setup_db_for_generate(
            mock_db, mock_user.id,
            jobs=[job], courses=[course], news_items=[news],
            existing_cache=None,
        )
        # match_jobs will be called for career_advice since no cache exists
        advisor.match_jobs.return_value = [{"job_id": job.id, "score": 85, "reasons": ["Match"]}]

        with patch.object(_router_module, "get_advisor", return_value=advisor):
            result = await generate_career_advice(current_user=mock_user, db=mock_db)

        assert result.career_direction == "Specializzati in AI/ML"
        assert len(result.recommended_courses) == 1
        assert len(result.recommended_articles) == 1
        assert "Docker" in result.skill_gaps

    @pytest.mark.asyncio
    async def test_raises_503_when_ai_unavailable(self, mock_db, mock_user):
        """Should raise 503 when Gemini is not available."""
        advisor = _mock_advisor(is_available=False)

        with patch.object(_router_module, "get_advisor", return_value=advisor):
            with pytest.raises(HTTPException) as exc_info:
                await generate_career_advice(current_user=mock_user, db=mock_db)
            assert exc_info.value.status_code == 503

    @pytest.mark.asyncio
    async def test_raises_503_when_gemini_returns_none(self, mock_db, mock_user):
        """Should raise 503 when Gemini fails to generate advice."""
        job = _make_job()
        advisor = _mock_advisor(match_result=[{"job_id": job.id, "score": 80, "reasons": []}], career_result=None)

        _setup_db_for_generate(mock_db, mock_user.id, jobs=[job], courses=[], news_items=[], existing_cache=None)

        with patch.object(_router_module, "get_advisor", return_value=advisor):
            with pytest.raises(HTTPException) as exc_info:
                await generate_career_advice(current_user=mock_user, db=mock_db)
            assert exc_info.value.status_code == 503

    @pytest.mark.asyncio
    async def test_uses_cached_job_matches(self, mock_db, mock_user):
        """Should use cached job matches instead of generating new ones."""
        job = _make_job()
        course = _make_course_item()
        news = _make_news_item()

        cached_matches = [{"job_id": job.id, "score": 85, "reasons": ["Cached match"]}]
        existing_cache = _make_cache(mock_user.id, "job_matches", cached_matches)

        career_result = {
            "career_direction": "Backend focus",
            "recommended_courses": [],
            "recommended_articles": [],
            "skill_gaps": ["Go"],
        }
        advisor = _mock_advisor(career_result=career_result)

        _setup_db_for_generate(
            mock_db, mock_user.id,
            jobs=[job], courses=[course], news_items=[news],
            existing_cache=existing_cache,
        )

        with patch.object(_router_module, "get_advisor", return_value=advisor):
            result = await generate_career_advice(current_user=mock_user, db=mock_db)

        assert result.career_direction == "Backend focus"
        # match_jobs should NOT have been called since cache exists
        advisor.match_jobs.assert_not_called()

    @pytest.mark.asyncio
    async def test_empty_courses_and_news(self, mock_db, mock_user):
        """Should handle case with no courses or news available."""
        career_result = {
            "career_direction": "Focus on learning",
            "recommended_courses": [],
            "recommended_articles": [],
            "skill_gaps": ["Everything"],
        }
        advisor = _mock_advisor(match_result=[], career_result=career_result)

        _setup_db_for_generate(
            mock_db, mock_user.id,
            jobs=[], courses=[], news_items=[], existing_cache=None,
        )

        with patch.object(_router_module, "get_advisor", return_value=advisor):
            result = await generate_career_advice(current_user=mock_user, db=mock_db)

        assert result.career_direction == "Focus on learning"
        assert result.recommended_courses == []
        assert result.recommended_articles == []

    @pytest.mark.asyncio
    async def test_with_multiple_courses_and_news(self, mock_db, mock_user):
        """Should handle multiple courses and news items."""
        courses = [_make_course_item(title=f"Course {i}") for i in range(5)]
        news_items = [_make_news_item(title=f"News {i}") for i in range(5)]

        career_result = {
            "career_direction": "Full stack AI",
            "recommended_courses": [
                {"course_id": courses[0].id, "reason": "Best AI course"},
                {"course_id": courses[1].id, "reason": "Good ML course"},
                {"course_id": courses[2].id, "reason": "DevOps fundamentals"},
            ],
            "recommended_articles": [
                {"news_id": news_items[0].id, "reason": "AI trends"},
                {"news_id": news_items[1].id, "reason": "Tech market"},
                {"news_id": news_items[2].id, "reason": "Career advice"},
            ],
            "skill_gaps": ["TensorFlow", "Docker", "AWS"],
        }
        advisor = _mock_advisor(match_result=[], career_result=career_result)

        _setup_db_for_generate(
            mock_db, mock_user.id,
            jobs=[], courses=courses, news_items=news_items, existing_cache=None,
        )

        with patch.object(_router_module, "get_advisor", return_value=advisor):
            result = await generate_career_advice(current_user=mock_user, db=mock_db)

        assert len(result.recommended_courses) == 3
        assert len(result.recommended_articles) == 3
        assert len(result.skill_gaps) == 3


# --- GET /ai/career-advice ---


class TestGetCachedCareerAdvice:
    """Tests for the GET /ai/career-advice endpoint."""

    @pytest.mark.asyncio
    async def test_returns_cached_advice(self, mock_db, mock_user):
        """Should return cached career advice when valid cache exists."""
        content = {
            "career_direction": "AI Engineer",
            "recommended_courses": [{"course_id": "c1", "reason": "Good"}],
            "recommended_articles": [{"news_id": "n1", "reason": "Useful"}],
            "skill_gaps": ["PyTorch"],
        }
        cache = _make_cache(mock_user.id, "career_advice", content)

        mock_db.query.return_value.filter.return_value.order_by.return_value.first.return_value = cache

        result = await get_cached_career_advice(current_user=mock_user, db=mock_db)

        assert result.career_direction == "AI Engineer"
        assert len(result.recommended_courses) == 1
        assert result.recommended_courses[0].course_id == "c1"
        assert len(result.recommended_articles) == 1
        assert result.recommended_articles[0].news_id == "n1"
        assert result.skill_gaps == ["PyTorch"]

    @pytest.mark.asyncio
    async def test_raises_404_when_no_cache(self, mock_db, mock_user):
        """Should raise 404 when no cached advice exists."""
        mock_db.query.return_value.filter.return_value.order_by.return_value.first.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            await get_cached_career_advice(current_user=mock_user, db=mock_db)
        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_raises_404_when_cache_expired(self, mock_db, mock_user):
        """Should raise 404 when cached advice is expired."""
        content = {"career_direction": "Old advice", "recommended_courses": [], "recommended_articles": [], "skill_gaps": []}
        cache = _make_cache(mock_user.id, "career_advice", content, expired=True)

        mock_db.query.return_value.filter.return_value.order_by.return_value.first.return_value = cache

        with pytest.raises(HTTPException) as exc_info:
            await get_cached_career_advice(current_user=mock_user, db=mock_db)
        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_returns_model_used(self, mock_db, mock_user):
        """Should return the model_used from cache."""
        content = {"career_direction": "Test", "recommended_courses": [], "recommended_articles": [], "skill_gaps": []}
        cache = _make_cache(mock_user.id, "career_advice", content, model_used="gemini-pro")

        mock_db.query.return_value.filter.return_value.order_by.return_value.first.return_value = cache

        result = await get_cached_career_advice(current_user=mock_user, db=mock_db)
        assert result.model_used == "gemini-pro"

    @pytest.mark.asyncio
    async def test_handles_naive_datetime_in_cache(self, mock_db, mock_user):
        """Should handle naive datetimes from SQLite cache."""
        content = {"career_direction": "Test", "recommended_courses": [], "recommended_articles": [], "skill_gaps": []}
        cache = _make_cache(mock_user.id, "career_advice", content, naive_datetime=True)

        mock_db.query.return_value.filter.return_value.order_by.return_value.first.return_value = cache

        result = await get_cached_career_advice(current_user=mock_user, db=mock_db)
        assert result.career_direction == "Test"

    @pytest.mark.asyncio
    async def test_handles_empty_recommended_lists(self, mock_db, mock_user):
        """Should handle empty recommended_courses and recommended_articles."""
        content = {"career_direction": "Generic", "recommended_courses": [], "recommended_articles": [], "skill_gaps": []}
        cache = _make_cache(mock_user.id, "career_advice", content)

        mock_db.query.return_value.filter.return_value.order_by.return_value.first.return_value = cache

        result = await get_cached_career_advice(current_user=mock_user, db=mock_db)
        assert result.recommended_courses == []
        assert result.recommended_articles == []
        assert result.skill_gaps == []

    @pytest.mark.asyncio
    async def test_handles_missing_keys_in_cache(self, mock_db, mock_user):
        """Should handle cached data with missing optional keys."""
        content = {"career_direction": "Partial data"}
        cache = _make_cache(mock_user.id, "career_advice", content)

        mock_db.query.return_value.filter.return_value.order_by.return_value.first.return_value = cache

        result = await get_cached_career_advice(current_user=mock_user, db=mock_db)
        assert result.career_direction == "Partial data"
        assert result.recommended_courses == []
        assert result.recommended_articles == []
        assert result.skill_gaps == []


# --- Schema validation tests ---


class TestAISchemas:
    """Tests for the AI Pydantic schemas."""

    def test_job_match_item_valid(self):
        """Should create a valid JobMatchItem."""
        from api.routes.ai.schemas import JobMatchItem
        item = JobMatchItem(job_id="abc", score=85, reasons=["Good match"])
        assert item.score == 85
        assert item.job_id == "abc"

    def test_job_match_item_score_bounds(self):
        """Should reject scores outside 0-100."""
        from api.routes.ai.schemas import JobMatchItem
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            JobMatchItem(job_id="abc", score=101, reasons=[])

        with pytest.raises(ValidationError):
            JobMatchItem(job_id="abc", score=-1, reasons=[])

    def test_job_match_response(self):
        """Should create a valid JobMatchResponse."""
        from api.routes.ai.schemas import JobMatchResponse, JobMatchItem
        now = datetime.now(timezone.utc)
        resp = JobMatchResponse(
            matches=[JobMatchItem(job_id="x", score=50, reasons=[])],
            generated_at=now,
            model_used="test-model",
        )
        assert len(resp.matches) == 1
        assert resp.model_used == "test-model"

    def test_career_advice_response(self):
        """Should create a valid CareerAdviceResponse."""
        from api.routes.ai.schemas import CareerAdviceResponse, RecommendedCourse, RecommendedArticle
        now = datetime.now(timezone.utc)
        resp = CareerAdviceResponse(
            career_direction="Go into AI",
            recommended_courses=[RecommendedCourse(course_id="c1", reason="Best course")],
            recommended_articles=[RecommendedArticle(news_id="n1", reason="Good article")],
            skill_gaps=["Python", "ML"],
            generated_at=now,
        )
        assert resp.career_direction == "Go into AI"
        assert len(resp.recommended_courses) == 1
        assert len(resp.recommended_articles) == 1
        assert len(resp.skill_gaps) == 2

    def test_recommended_course_requires_fields(self):
        """Should require course_id and reason."""
        from api.routes.ai.schemas import RecommendedCourse
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            RecommendedCourse(course_id="c1")  # missing reason

    def test_recommended_article_requires_fields(self):
        """Should require news_id and reason."""
        from api.routes.ai.schemas import RecommendedArticle
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            RecommendedArticle(news_id="n1")  # missing reason


# --- GeminiAdvisor unit tests ---


class TestGeminiAdvisorService:
    """Tests for the GeminiAdvisor service (mocked)."""

    def test_advisor_not_available_without_api_key(self):
        """Should report unavailable when no API key is set."""
        from api.services.ai_advisor import GeminiAdvisor

        # Reset singleton
        GeminiAdvisor._instance = None
        with patch.dict("os.environ", {}, clear=True):
            # Ensure GOOGLE_API_KEY is not present
            import os
            old = os.environ.pop("GOOGLE_API_KEY", None)
            try:
                advisor = GeminiAdvisor()
                assert not advisor.is_available
            finally:
                GeminiAdvisor._instance = None
                if old is not None:
                    os.environ["GOOGLE_API_KEY"] = old

    def test_parse_json_valid(self):
        """Should parse valid JSON."""
        from api.services.ai_advisor import GeminiAdvisor
        GeminiAdvisor._instance = None
        advisor = GeminiAdvisor.__new__(GeminiAdvisor)
        advisor._initialized = True
        advisor._api_key = None
        advisor._client = None
        advisor._model = "test"

        result = advisor._parse_json('[{"a": 1}]', fallback=[])
        assert result == [{"a": 1}]

    def test_parse_json_invalid(self):
        """Should return fallback on invalid JSON."""
        from api.services.ai_advisor import GeminiAdvisor
        advisor = GeminiAdvisor.__new__(GeminiAdvisor)
        advisor._initialized = True
        advisor._api_key = None
        advisor._client = None
        advisor._model = "test"

        result = advisor._parse_json("not json", fallback=[])
        assert result == []

    def test_parse_json_none(self):
        """Should return fallback on None input."""
        from api.services.ai_advisor import GeminiAdvisor
        advisor = GeminiAdvisor.__new__(GeminiAdvisor)
        advisor._initialized = True
        advisor._api_key = None
        advisor._client = None
        advisor._model = "test"

        result = advisor._parse_json(None, fallback={"default": True})
        assert result == {"default": True}

    def test_match_jobs_returns_none_when_unavailable(self):
        """Should return None when advisor is not available."""
        from api.services.ai_advisor import GeminiAdvisor
        advisor = GeminiAdvisor.__new__(GeminiAdvisor)
        advisor._initialized = True
        advisor._api_key = None
        advisor._client = None
        advisor._model = "test"

        result = advisor.match_jobs({"skills": []}, [{"job_id": "1"}])
        assert result is None

    def test_career_recommendations_returns_none_when_unavailable(self):
        """Should return None when advisor is not available."""
        from api.services.ai_advisor import GeminiAdvisor
        advisor = GeminiAdvisor.__new__(GeminiAdvisor)
        advisor._initialized = True
        advisor._api_key = None
        advisor._client = None
        advisor._model = "test"

        result = advisor.career_recommendations({"skills": []}, [], [], [])
        assert result is None
