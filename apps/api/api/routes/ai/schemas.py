"""Pydantic schemas for AI-powered job matching and career recommendations."""

from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class JobMatchItem(BaseModel):
    job_id: str
    score: int = Field(..., ge=0, le=100)
    reasons: list[str] = Field(default_factory=list)


class JobMatchResponse(BaseModel):
    matches: list[JobMatchItem] = Field(default_factory=list)
    generated_at: datetime
    model_used: Optional[str] = None


class RecommendedCourse(BaseModel):
    course_id: str
    reason: str


class RecommendedArticle(BaseModel):
    news_id: str
    reason: str


class CareerAdviceResponse(BaseModel):
    career_direction: str
    recommended_courses: list[RecommendedCourse] = Field(default_factory=list)
    recommended_articles: list[RecommendedArticle] = Field(default_factory=list)
    skill_gaps: list[str] = Field(default_factory=list)
    generated_at: datetime
    model_used: Optional[str] = None
