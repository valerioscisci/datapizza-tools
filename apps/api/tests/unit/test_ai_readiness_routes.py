"""Tests for AI Readiness assessment feature.

Covers:
- questions.py: compute_score, get_weak_categories
- schemas.py: QuizSubmission validation
- router.py: all 4 endpoints (GET /quiz, POST /, GET /, GET /suggestions)
- Profile integration: ai_readiness fields in ProfileResponse
- Talents integration: ai_readiness filter in list_talents
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from api.routes.profile.ai_readiness.questions import (
    QUIZ_QUESTIONS,
    QUIZ_VERSION,
    VALID_QUESTION_IDS,
    compute_score,
    get_weak_categories,
)
from api.routes.profile.ai_readiness.schemas import (
    AssessmentResponse,
    CourseSuggestion,
    QuizMetaResponse,
    QuizQuestionMeta,
    QuizSubmission,
    SuggestionsResponse,
)
from api.routes.profile.ai_readiness.router import (
    get_assessment,
    get_quiz,
    get_suggestions,
    submit_quiz,
)


# ---------------------------------------------------------------------------
# Helper: build a valid answer dict
# ---------------------------------------------------------------------------
def _valid_answers(value: int = 2) -> dict[str, int]:
    """Return a valid answer dict with all questions set to the given value."""
    return {q["id"]: value for q in QUIZ_QUESTIONS}


# ===========================================================================
# 1. questions.py — compute_score
# ===========================================================================
class TestComputeScore:
    """Tests for the compute_score function."""

    def test_all_zeros_gives_zero_beginner(self):
        """All answers=0 -> score=0, level=beginner."""
        score, level = compute_score(_valid_answers(0))
        assert score == 0
        assert level == "beginner"

    def test_all_fours_gives_100_expert(self):
        """All answers=4 -> score=100, level=expert."""
        score, level = compute_score(_valid_answers(4))
        assert score == 100
        assert level == "expert"

    def test_boundary_beginner_25(self):
        """Score=25 should be beginner (boundary)."""
        # raw=8 -> 8/32*100 = 25
        answers = _valid_answers(1)
        score, level = compute_score(answers)
        assert score == 25
        assert level == "beginner"

    def test_boundary_intermediate_26(self):
        """Score just above 25 should be intermediate."""
        # raw=9 -> 9/32*100 = 28.125 rounds to 28 -> intermediate
        answers = _valid_answers(1)
        answers["q1_ai_coding_assistants"] = 2  # bump one to push over 25
        score, level = compute_score(answers)
        assert score == 28
        assert level == "intermediate"

    def test_boundary_intermediate_50(self):
        """Score=50 should be intermediate (boundary)."""
        # raw=16 -> 16/32*100 = 50
        answers = _valid_answers(2)
        score, level = compute_score(answers)
        assert score == 50
        assert level == "intermediate"

    def test_boundary_advanced_51(self):
        """Score just above 50 should be advanced."""
        # raw=17 -> 17/32*100 = 53.125 rounds to 53 -> advanced
        answers = _valid_answers(2)
        answers["q1_ai_coding_assistants"] = 3
        score, level = compute_score(answers)
        assert score == 53
        assert level == "advanced"

    def test_boundary_advanced_75(self):
        """Score=75 should be advanced (boundary)."""
        # raw=24 -> 24/32*100 = 75
        answers = _valid_answers(3)
        score, level = compute_score(answers)
        assert score == 75
        assert level == "advanced"

    def test_boundary_expert_76(self):
        """Score just above 75 should be expert."""
        # raw=25 -> 25/32*100 = 78.125 rounds to 78 -> expert
        answers = _valid_answers(3)
        answers["q1_ai_coding_assistants"] = 4
        score, level = compute_score(answers)
        assert score == 78
        assert level == "expert"

    def test_midpoint_score(self):
        """Mixed answers produce correct percentage."""
        answers = {
            "q1_ai_coding_assistants": 4,
            "q2_prompt_writing": 3,
            "q3_agentic_workflows": 2,
            "q4_ai_code_review": 1,
            "q5_ai_api_integration": 0,
            "q6_ai_output_evaluation": 4,
            "q7_rag_systems": 3,
            "q8_prompt_engineering": 2,
        }
        # raw = 4+3+2+1+0+4+3+2 = 19, pct = round(19/32*100) = 59
        score, level = compute_score(answers)
        assert score == 59
        assert level == "advanced"


# ===========================================================================
# 2. questions.py — get_weak_categories
# ===========================================================================
class TestGetWeakCategories:
    """Tests for the get_weak_categories function."""

    def test_no_weak_areas(self):
        """All answers >= threshold -> no weak categories."""
        assert get_weak_categories(_valid_answers(2)) == []

    def test_all_weak(self):
        """All answers=0 -> all categories flagged."""
        cats = get_weak_categories(_valid_answers(0))
        assert set(cats) == {"AI", "ML", "tech", "backend"}

    def test_single_weak_question(self):
        """One question below threshold -> its categories are flagged."""
        answers = _valid_answers(3)
        answers["q6_ai_output_evaluation"] = 1  # categories: ["ML"]
        cats = get_weak_categories(answers)
        assert cats == ["ML"]

    def test_multiple_weak_questions_deduplicated(self):
        """Multiple weak questions sharing a category -> deduplicated."""
        answers = _valid_answers(3)
        answers["q1_ai_coding_assistants"] = 0  # AI
        answers["q2_prompt_writing"] = 1  # AI
        cats = get_weak_categories(answers)
        assert cats == ["AI"]

    def test_custom_threshold(self):
        """Higher threshold flags more categories."""
        answers = _valid_answers(2)
        cats_default = get_weak_categories(answers, threshold=2)
        cats_higher = get_weak_categories(answers, threshold=3)
        assert len(cats_default) == 0
        assert len(cats_higher) > 0

    def test_unknown_question_id_ignored(self):
        """Unknown question IDs are silently ignored."""
        answers = {"unknown_q": 0}
        assert get_weak_categories(answers) == []

    def test_returns_sorted(self):
        """Weak categories are returned in sorted order."""
        answers = _valid_answers(0)
        cats = get_weak_categories(answers)
        assert cats == sorted(cats)


# ===========================================================================
# 3. schemas.py — QuizSubmission validation
# ===========================================================================
class TestQuizSubmissionValidation:
    """Tests for QuizSubmission Pydantic schema validation."""

    def test_valid_submission(self):
        """Valid answers pass validation."""
        sub = QuizSubmission(answers=_valid_answers(2))
        assert len(sub.answers) == 8

    def test_missing_keys_raises(self):
        """Submission with missing question IDs raises ValidationError."""
        partial = dict(list(_valid_answers(2).items())[:5])
        with pytest.raises(ValidationError) as exc_info:
            QuizSubmission(answers=partial)
        assert "Missing required question" in str(exc_info.value)

    def test_extra_keys_raises(self):
        """Submission with unknown question IDs raises ValidationError."""
        answers = _valid_answers(2)
        answers["q99_unknown"] = 3
        with pytest.raises(ValidationError) as exc_info:
            QuizSubmission(answers=answers)
        assert "Unknown question" in str(exc_info.value)

    def test_value_below_zero_raises(self):
        """Answer value < 0 raises ValidationError."""
        answers = _valid_answers(2)
        answers["q1_ai_coding_assistants"] = -1
        with pytest.raises(ValidationError) as exc_info:
            QuizSubmission(answers=answers)
        assert "between 0 and 4" in str(exc_info.value)

    def test_value_above_four_raises(self):
        """Answer value > 4 raises ValidationError."""
        answers = _valid_answers(2)
        answers["q1_ai_coding_assistants"] = 5
        with pytest.raises(ValidationError) as exc_info:
            QuizSubmission(answers=answers)
        assert "between 0 and 4" in str(exc_info.value)

    def test_empty_answers_raises(self):
        """Empty answers dict raises ValidationError for missing keys."""
        with pytest.raises(ValidationError) as exc_info:
            QuizSubmission(answers={})
        assert "Missing required question" in str(exc_info.value)

    def test_all_zeros_valid(self):
        """All answers=0 is a valid submission."""
        sub = QuizSubmission(answers=_valid_answers(0))
        assert all(v == 0 for v in sub.answers.values())

    def test_all_fours_valid(self):
        """All answers=4 is a valid submission."""
        sub = QuizSubmission(answers=_valid_answers(4))
        assert all(v == 4 for v in sub.answers.values())


# ===========================================================================
# 4. router.py — GET /quiz
# ===========================================================================
class TestGetQuiz:
    """Tests for the GET /profile/ai-readiness/quiz endpoint."""

    @pytest.mark.asyncio
    async def test_returns_8_questions_and_version(self, mock_user):
        """GET /quiz returns 8 question IDs and the current version."""
        result = await get_quiz(current_user=mock_user)

        assert isinstance(result, QuizMetaResponse)
        assert len(result.questions) == 8
        assert result.version == QUIZ_VERSION
        assert all(isinstance(q, QuizQuestionMeta) for q in result.questions)

    @pytest.mark.asyncio
    async def test_question_ids_match_constants(self, mock_user):
        """GET /quiz question IDs match the QUIZ_QUESTIONS constant."""
        result = await get_quiz(current_user=mock_user)
        returned_ids = {q.id for q in result.questions}
        assert returned_ids == VALID_QUESTION_IDS


# ===========================================================================
# 5. router.py — POST /
# ===========================================================================
class TestSubmitQuiz:
    """Tests for the POST /profile/ai-readiness endpoint."""

    @pytest.mark.asyncio
    async def test_submit_valid_answers(self, mock_user, mock_db):
        """Valid submission creates assessment and returns result."""
        data = QuizSubmission(answers=_valid_answers(3))
        result = await submit_quiz(data=data, current_user=mock_user, db=mock_db)

        assert isinstance(result, AssessmentResponse)
        assert result.total_score == 75
        assert result.readiness_level == "advanced"
        assert result.quiz_version == QUIZ_VERSION
        assert result.answers == _valid_answers(3)

        # Verify DB interactions
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_submit_updates_user_fields(self, mock_user, mock_db):
        """Submission updates user's denormalized ai_readiness fields."""
        data = QuizSubmission(answers=_valid_answers(4))
        await submit_quiz(data=data, current_user=mock_user, db=mock_db)

        assert mock_user.ai_readiness_score == 100
        assert mock_user.ai_readiness_level == "expert"

    @pytest.mark.asyncio
    async def test_company_user_gets_403(self, mock_company_user, mock_db):
        """Company users receive 403 Forbidden."""
        data = QuizSubmission(answers=_valid_answers(2))

        with pytest.raises(HTTPException) as exc_info:
            await submit_quiz(data=data, current_user=mock_company_user, db=mock_db)

        assert exc_info.value.status_code == 403
        assert "Only talent users" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_retake_creates_new_assessment(self, mock_user, mock_db):
        """Retaking the quiz creates a new assessment (old ones preserved in DB)."""
        data1 = QuizSubmission(answers=_valid_answers(1))
        await submit_quiz(data=data1, current_user=mock_user, db=mock_db)
        assert mock_user.ai_readiness_score == 25

        # Reset mock call counts
        mock_db.reset_mock()

        data2 = QuizSubmission(answers=_valid_answers(4))
        await submit_quiz(data=data2, current_user=mock_user, db=mock_db)
        assert mock_user.ai_readiness_score == 100
        assert mock_user.ai_readiness_level == "expert"

        # Second submission also calls add + commit + refresh
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_submit_all_zeros(self, mock_user, mock_db):
        """All zeros produces score=0, level=beginner."""
        data = QuizSubmission(answers=_valid_answers(0))
        result = await submit_quiz(data=data, current_user=mock_user, db=mock_db)
        assert result.total_score == 0
        assert result.readiness_level == "beginner"


# ===========================================================================
# 6. router.py — GET /
# ===========================================================================
class TestGetAssessment:
    """Tests for the GET /profile/ai-readiness endpoint."""

    @pytest.mark.asyncio
    async def test_returns_latest_assessment(self, mock_user, mock_db):
        """GET / returns the most recent assessment for the current user."""
        mock_assessment = MagicMock()
        mock_assessment.id = str(uuid4())
        mock_assessment.user_id = mock_user.id
        mock_assessment.answers_json = json.dumps(_valid_answers(3))
        mock_assessment.total_score = 75
        mock_assessment.readiness_level = "advanced"
        mock_assessment.quiz_version = 1
        mock_assessment.created_at = datetime(2024, 6, 1, tzinfo=timezone.utc)

        mock_db.query.return_value.filter.return_value.order_by.return_value.first.return_value = mock_assessment

        result = await get_assessment(current_user=mock_user, db=mock_db)

        assert isinstance(result, AssessmentResponse)
        assert result.total_score == 75
        assert result.readiness_level == "advanced"
        assert result.answers == _valid_answers(3)

    @pytest.mark.asyncio
    async def test_returns_404_when_no_assessment(self, mock_user, mock_db):
        """GET / returns 404 when user has never taken the quiz."""
        mock_db.query.return_value.filter.return_value.order_by.return_value.first.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            await get_assessment(current_user=mock_user, db=mock_db)

        assert exc_info.value.status_code == 404
        assert "No AI readiness assessment found" in exc_info.value.detail


# ===========================================================================
# 7. router.py — GET /suggestions
# ===========================================================================
class TestGetSuggestions:
    """Tests for the GET /profile/ai-readiness/suggestions endpoint."""

    @pytest.mark.asyncio
    async def test_returns_suggestions_for_weak_areas(self, mock_user, mock_db):
        """GET /suggestions returns courses matching weak categories."""
        # Assessment with weak areas (q6 ML category scored 0)
        answers = _valid_answers(3)
        answers["q6_ai_output_evaluation"] = 0

        mock_assessment = MagicMock()
        mock_assessment.answers_json = json.dumps(answers)

        mock_course = MagicMock()
        mock_course.id = str(uuid4())
        mock_course.title = "Intro to ML"
        mock_course.provider = "Coursera"
        mock_course.level = "beginner"
        mock_course.url = "https://coursera.org/ml"
        mock_course.category = "ML"

        # Setup query chain: assessment query -> course query
        assessment_query = MagicMock()
        assessment_query.filter.return_value.order_by.return_value.first.return_value = mock_assessment

        course_query = MagicMock()
        course_query.filter.return_value.order_by.return_value.limit.return_value.all.return_value = [mock_course]

        call_count = [0]

        def query_side_effect(model):
            call_count[0] += 1
            if call_count[0] == 1:
                return assessment_query
            return course_query

        mock_db.query.side_effect = query_side_effect

        result = await get_suggestions(current_user=mock_user, db=mock_db)

        assert isinstance(result, SuggestionsResponse)
        assert len(result.suggestions) == 1
        assert result.suggestions[0].title == "Intro to ML"
        assert "ML" in result.weak_categories

    @pytest.mark.asyncio
    async def test_returns_404_when_no_assessment(self, mock_user, mock_db):
        """GET /suggestions returns 404 when user has no assessment."""
        mock_db.query.return_value.filter.return_value.order_by.return_value.first.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            await get_suggestions(current_user=mock_user, db=mock_db)

        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_no_weak_areas_returns_empty(self, mock_user, mock_db):
        """GET /suggestions with all high scores returns empty suggestions."""
        mock_assessment = MagicMock()
        mock_assessment.answers_json = json.dumps(_valid_answers(4))

        mock_db.query.return_value.filter.return_value.order_by.return_value.first.return_value = mock_assessment

        result = await get_suggestions(current_user=mock_user, db=mock_db)

        assert result.suggestions == []
        assert result.weak_categories == []

    @pytest.mark.asyncio
    async def test_no_courses_match_weak_categories(self, mock_user, mock_db):
        """GET /suggestions with weak areas but no matching courses returns empty list."""
        answers = _valid_answers(0)  # all weak
        mock_assessment = MagicMock()
        mock_assessment.answers_json = json.dumps(answers)

        assessment_query = MagicMock()
        assessment_query.filter.return_value.order_by.return_value.first.return_value = mock_assessment

        course_query = MagicMock()
        course_query.filter.return_value.order_by.return_value.limit.return_value.all.return_value = []

        call_count = [0]

        def query_side_effect(model):
            call_count[0] += 1
            if call_count[0] == 1:
                return assessment_query
            return course_query

        mock_db.query.side_effect = query_side_effect

        result = await get_suggestions(current_user=mock_user, db=mock_db)

        assert result.suggestions == []
        assert len(result.weak_categories) > 0  # weak categories identified even if no courses


# ===========================================================================
# 8. Profile integration
# ===========================================================================
class TestProfileIntegration:
    """Tests for ai_readiness fields in ProfileResponse."""

    def test_profile_response_includes_ai_readiness_fields(self):
        """ProfileResponse schema includes ai_readiness_score and ai_readiness_level."""
        from api.routes.profile.schemas import ProfileResponse

        fields = ProfileResponse.model_fields
        assert "ai_readiness_score" in fields
        assert "ai_readiness_level" in fields

    @pytest.mark.asyncio
    async def test_build_profile_includes_ai_readiness(self, mock_user):
        """_build_profile_response includes ai_readiness fields from user."""
        from api.routes.profile.router import _build_profile_response

        mock_user.ai_readiness_score = 84
        mock_user.ai_readiness_level = "expert"

        result = _build_profile_response(mock_user, [], [])
        assert result.ai_readiness_score == 84
        assert result.ai_readiness_level == "expert"

    @pytest.mark.asyncio
    async def test_build_profile_ai_readiness_null(self, mock_user):
        """_build_profile_response handles null ai_readiness fields."""
        from api.routes.profile.router import _build_profile_response

        mock_user.ai_readiness_score = None
        mock_user.ai_readiness_level = None

        result = _build_profile_response(mock_user, [], [])
        assert result.ai_readiness_score is None
        assert result.ai_readiness_level is None


# ===========================================================================
# 9. Talents integration — filter by ai_readiness_level
# ===========================================================================
class TestTalentsAIReadinessFilter:
    """Tests for ai_readiness filter in list_talents."""

    @pytest.mark.asyncio
    async def test_filter_by_ai_readiness_level(self, mock_db, mock_public_user):
        """list_talents with ai_readiness filter chains an additional .filter call."""
        from api.routes.talents.router import list_talents

        mock_public_user.ai_readiness_score = 84
        mock_public_user.ai_readiness_level = "expert"

        query_mock = MagicMock()
        mock_db.query.return_value.filter.return_value = query_mock

        filtered_mock = MagicMock()
        query_mock.filter.return_value = filtered_mock
        filtered_mock.count.return_value = 1
        filtered_mock.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [mock_public_user]

        result = await list_talents(
            page=1, page_size=10, search=None, skills=None,
            availability=None, experience_level=None, location=None,
            ai_readiness="expert", db=mock_db,
        )

        query_mock.filter.assert_called()
        assert result.total == 1
        assert result.items[0].ai_readiness_level == "expert"

    @pytest.mark.asyncio
    async def test_talent_card_includes_ai_readiness_fields(self, mock_db, mock_public_user):
        """Talent card response includes ai_readiness fields."""
        from api.routes.talents.router import list_talents

        mock_public_user.ai_readiness_score = 62
        mock_public_user.ai_readiness_level = "advanced"

        query_mock = MagicMock()
        mock_db.query.return_value.filter.return_value = query_mock
        query_mock.count.return_value = 1
        query_mock.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [mock_public_user]

        result = await list_talents(
            page=1, page_size=10, search=None, skills=None,
            availability=None, experience_level=None, location=None,
            ai_readiness=None, db=mock_db,
        )

        assert result.items[0].ai_readiness_score == 62
        assert result.items[0].ai_readiness_level == "advanced"

    @pytest.mark.asyncio
    async def test_talent_card_null_ai_readiness(self, mock_db, mock_public_user):
        """Talent card handles null ai_readiness fields (user never took quiz)."""
        from api.routes.talents.router import list_talents

        mock_public_user.ai_readiness_score = None
        mock_public_user.ai_readiness_level = None

        query_mock = MagicMock()
        mock_db.query.return_value.filter.return_value = query_mock
        query_mock.count.return_value = 1
        query_mock.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [mock_public_user]

        result = await list_talents(
            page=1, page_size=10, search=None, skills=None,
            availability=None, experience_level=None, location=None,
            ai_readiness=None, db=mock_db,
        )

        assert result.items[0].ai_readiness_score is None
        assert result.items[0].ai_readiness_level is None

    @pytest.mark.asyncio
    async def test_talent_detail_includes_ai_readiness(self, mock_db, mock_public_user):
        """get_talent response includes ai_readiness fields."""
        from api.routes.talents.router import get_talent

        mock_public_user.ai_readiness_score = 44
        mock_public_user.ai_readiness_level = "intermediate"

        user_query = MagicMock()
        user_query.first.return_value = mock_public_user

        empty_query = MagicMock()
        empty_query.order_by.return_value.all.return_value = []

        def query_side_effect(model):
            q = MagicMock()
            if hasattr(model, '__tablename__'):
                if model.__tablename__ == "users":
                    q.filter.return_value = user_query
                else:
                    q.filter.return_value = empty_query
            else:
                name = getattr(model, '__name__', '')
                if name == 'User':
                    q.filter.return_value = user_query
                else:
                    q.filter.return_value = empty_query
            return q

        mock_db.query.side_effect = query_side_effect

        result = await get_talent(talent_id=mock_public_user.id, db=mock_db)

        assert result.ai_readiness_score == 44
        assert result.ai_readiness_level == "intermediate"


# ===========================================================================
# 10. Schema response models
# ===========================================================================
class TestResponseSchemas:
    """Tests for response schema models."""

    def test_assessment_response_from_attributes(self):
        """AssessmentResponse can be created with from_attributes."""
        data = AssessmentResponse(
            id="test-id",
            total_score=75,
            readiness_level="advanced",
            answers=_valid_answers(3),
            quiz_version=1,
            created_at=datetime.now(timezone.utc),
        )
        assert data.total_score == 75

    def test_course_suggestion_schema(self):
        """CourseSuggestion schema works correctly."""
        suggestion = CourseSuggestion(
            id="course-1",
            title="Intro to AI",
            provider="Coursera",
            level="beginner",
            url="https://coursera.org/ai",
            category="AI",
        )
        assert suggestion.title == "Intro to AI"

    def test_suggestions_response_empty(self):
        """SuggestionsResponse with empty lists is valid."""
        resp = SuggestionsResponse(suggestions=[], weak_categories=[])
        assert resp.suggestions == []
        assert resp.weak_categories == []

    def test_quiz_meta_response(self):
        """QuizMetaResponse schema works correctly."""
        resp = QuizMetaResponse(
            questions=[QuizQuestionMeta(id="q1")],
            version=1,
        )
        assert len(resp.questions) == 1
        assert resp.version == 1


# ===========================================================================
# 11. Talent detail schema validation
# ===========================================================================
class TestTalentSchemas:
    """Tests for TalentCardResponse and TalentDetailResponse with ai_readiness."""

    def test_talent_card_response_has_ai_readiness_fields(self):
        """TalentCardResponse schema includes ai_readiness fields."""
        from api.routes.talents.schemas import TalentCardResponse

        fields = TalentCardResponse.model_fields
        assert "ai_readiness_score" in fields
        assert "ai_readiness_level" in fields

    def test_talent_detail_response_has_ai_readiness_fields(self):
        """TalentDetailResponse schema includes ai_readiness fields."""
        from api.routes.talents.schemas import TalentDetailResponse

        fields = TalentDetailResponse.model_fields
        assert "ai_readiness_score" in fields
        assert "ai_readiness_level" in fields
