"""Pydantic schemas for the AI Readiness assessment endpoints."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from api.routes.profile.ai_readiness.questions import VALID_QUESTION_IDS


class QuizQuestionMeta(BaseModel):
    """Metadata for a single quiz question (ID only; text is rendered client-side via i18n)."""

    id: str = Field(description="Unique question identifier, used as i18n key")


class QuizMetaResponse(BaseModel):
    """Response for GET /quiz — returns question IDs and quiz version."""

    questions: list[QuizQuestionMeta] = Field(description="Ordered list of question metadata")
    version: int = Field(description="Quiz version number for answer compatibility")


class QuizSubmission(BaseModel):
    """Request body for POST /ai-readiness — submitting quiz answers."""

    answers: dict[str, int] = Field(
        description="Map of question ID to answer value (0-4). All 8 questions required."
    )

    @field_validator("answers")
    @classmethod
    def validate_answers(cls, v: dict[str, int]) -> dict[str, int]:
        # Check all required keys are present
        missing = VALID_QUESTION_IDS - set(v.keys())
        if missing:
            raise ValueError(f"Missing required question(s): {', '.join(sorted(missing))}")

        # Check no extra keys
        extra = set(v.keys()) - VALID_QUESTION_IDS
        if extra:
            raise ValueError(f"Unknown question(s): {', '.join(sorted(extra))}")

        # Check values in range 0-4
        for qid, val in v.items():
            if not isinstance(val, int) or val < 0 or val > 4:
                raise ValueError(f"Answer for '{qid}' must be an integer between 0 and 4, got {val}")

        return v


class AssessmentResponse(BaseModel):
    """Response for GET/POST /ai-readiness — assessment result."""

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(description="Assessment record ID")
    total_score: int = Field(description="Score as percentage (0-100)")
    readiness_level: str = Field(description="Level: beginner, intermediate, advanced, or expert")
    answers: dict[str, int] = Field(description="Original answers submitted")
    quiz_version: int = Field(description="Version of the quiz taken")
    created_at: datetime = Field(description="When the assessment was submitted")


class CourseSuggestion(BaseModel):
    """A course suggested based on weak quiz areas."""

    id: str = Field(description="Course ID")
    title: str = Field(description="Course title")
    provider: str = Field(description="Course provider (e.g. Coursera, Udemy)")
    level: str = Field(description="Course difficulty level")
    url: str = Field(description="Direct URL to the course")
    category: str = Field(description="Course category (AI, ML, etc.)")


class SuggestionsResponse(BaseModel):
    """Response for GET /ai-readiness/suggestions."""

    suggestions: list[CourseSuggestion] = Field(description="Recommended courses for weak areas")
    weak_categories: list[str] = Field(description="Categories where the user scored below threshold")
