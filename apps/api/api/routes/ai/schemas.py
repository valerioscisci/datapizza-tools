"""Pydantic schemas for AI-powered job matching and career recommendations."""

from __future__ import annotations

from typing import Literal
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


# --- Skill Gap Analysis Schemas ---


class SkillDemandStatus(BaseModel):
    """A single user skill with its market demand status."""
    skill: str = Field(description="Skill name (e.g. 'React')")
    demand_status: Literal["green", "yellow", "red"] = Field(description="Color status: 'green' (in demand), 'yellow' (stable), 'red' (declining)")
    trend_direction: Literal["up", "down", "stable"] = Field(description="Trend: 'up', 'down', or 'stable'")
    trend_percentage: float = Field(description="Demand change percentage (e.g. +15.0, -8.5, 0.0)")
    job_count: int = Field(description="Number of active jobs requiring this skill")


class MissingSkill(BaseModel):
    """A skill the user is missing that is in demand."""
    skill: str = Field(description="Skill name")
    demand_level: Literal["high", "medium", "low"] = Field(description="'high', 'medium', or 'low'")
    job_count: int = Field(description="Number of jobs requiring this skill")
    recommended_courses: list[str] = Field(
        default_factory=list,
        description="Course IDs from the catalog that teach this skill"
    )
    reason: str = Field(default="", description="AI-generated reason why this skill matters")


class MarketTrend(BaseModel):
    """A skill's market trend data."""
    skill: str = Field(description="Skill name")
    direction: Literal["up", "down", "stable"] = Field(description="'up', 'down', or 'stable'")
    change_percentage: float = Field(description="Change percentage over the comparison period")
    job_count: int = Field(description="Current number of jobs requiring this skill")


class SkillGapAnalysisResponse(BaseModel):
    """Full skill gap analysis response."""
    user_skills: list[SkillDemandStatus] = Field(
        default_factory=list,
        description="User's current skills with market demand status"
    )
    missing_skills: list[MissingSkill] = Field(
        default_factory=list,
        description="Skills in demand that the user lacks"
    )
    market_trends: list[MarketTrend] = Field(
        default_factory=list,
        description="Top trending skills in the market"
    )
    personalized_insights: Optional[str] = Field(
        None,
        description="AI-generated personalized summary in Italian (null if AI unavailable)"
    )
    no_skills_warning: bool = Field(
        default=False,
        description="True if user has no skills in their profile"
    )
    ai_unavailable: bool = Field(
        default=False,
        description="True if Gemini was unavailable (algorithmic data still returned)"
    )
    generated_at: datetime = Field(description="When the analysis was generated or cached")
    model_used: Optional[str] = Field(None, description="AI model used (e.g. 'gemini-2.0-flash')")


class MarketTrendsResponse(BaseModel):
    """Global market trends response (not per-user)."""
    trends: list[MarketTrend] = Field(
        default_factory=list,
        description="All skills ranked by demand"
    )
    total_active_jobs: int = Field(description="Total number of active jobs analyzed")
    generated_at: datetime = Field(description="When the trends were computed")
