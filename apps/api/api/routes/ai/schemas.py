"""Pydantic schemas for AI-powered job matching and career recommendations."""

from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class JobMatchItem(BaseModel):
    job_id: str = Field(description="ID of the matched job")
    score: int = Field(..., ge=0, le=100, description="Match score from 0 (no fit) to 100 (perfect fit)")
    reasons: list[str] = Field(default_factory=list, description="AI-generated explanations for the match score")


class JobMatchResponse(BaseModel):
    matches: list[JobMatchItem] = Field(default_factory=list, description="Ranked list of job matches")
    generated_at: datetime = Field(description="When the matches were generated or cached")
    model_used: Optional[str] = Field(None, description="AI model used for generation (e.g. 'gemini-2.0-flash')")


class RecommendedCourse(BaseModel):
    course_id: str = Field(description="ID of the recommended course")
    reason: str = Field(description="AI-generated explanation for why this course is recommended")


class RecommendedArticle(BaseModel):
    news_id: str = Field(description="ID of the recommended news article")
    reason: str = Field(description="AI-generated explanation for why this article is relevant")


class CareerAdviceResponse(BaseModel):
    career_direction: str = Field(description="AI-suggested career direction summary")
    recommended_courses: list[RecommendedCourse] = Field(default_factory=list, description="Courses recommended to fill skill gaps")
    recommended_articles: list[RecommendedArticle] = Field(default_factory=list, description="Relevant industry articles and news")
    skill_gaps: list[str] = Field(default_factory=list, description="Skills the user should develop")
    generated_at: datetime = Field(description="When the advice was generated or cached")
    model_used: Optional[str] = Field(None, description="AI model used for generation (e.g. 'gemini-2.0-flash')")
