from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class MilestoneResponse(BaseModel):
    id: str = Field(description="Unique milestone identifier")
    milestone_type: str = Field(description="Milestone category (course_completed, 25_percent, streak_3, etc.)")
    title: str = Field(description="Human-readable milestone title")
    description: Optional[str] = Field(None, description="Optional detailed description")
    xp_reward: int = Field(0, description="XP points awarded for this milestone")
    achieved_at: datetime = Field(description="When the milestone was achieved")


class ProposalCourseResponse(BaseModel):
    id: str = Field(description="Unique proposal-course link identifier")
    course_id: str = Field(description="Referenced course identifier")
    course_title: str = Field(description="Course title")
    course_provider: str = Field(description="Course provider (e.g. Udemy, Coursera)")
    course_level: str = Field(description="Difficulty level (beginner, intermediate, advanced)")
    course_url: Optional[str] = Field(None, description="Direct URL to the course")
    course_duration: Optional[str] = Field(None, description="Estimated duration (e.g. '10 hours')")
    course_category: Optional[str] = Field(None, description="Course category (e.g. 'Python', 'DevOps')")
    order: int = Field(description="Position in the learning path (0-based)")
    is_completed: bool = Field(description="Whether the talent has completed this course")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")
    started_at: Optional[datetime] = Field(None, description="When the talent started the course")
    talent_notes: Optional[str] = Field(None, description="Notes written by the talent")
    company_notes: Optional[str] = Field(None, description="Notes written by the company")
    deadline: Optional[datetime] = Field(None, description="Company-set deadline for completion")
    xp_earned: int = Field(0, description="XP earned upon completion")
    is_overdue: bool = Field(False, description="True if the deadline has passed and the course is not completed")
    days_remaining: Optional[int] = Field(None, description="Days until deadline (negative if overdue)")


class ProposalCreate(BaseModel):
    talent_id: str = Field(..., min_length=1, description="ID of the talent to send the proposal to")
    message: Optional[str] = Field(None, description="Cover message from the company to the talent")
    budget_range: Optional[str] = Field(None, max_length=100, description="Budget range (e.g. '5000-10000 EUR')")
    course_ids: list[str] = Field(..., min_length=1, description="Ordered list of course IDs forming the learning path")


class ProposalUpdate(BaseModel):
    status: Optional[str] = Field(None, pattern=r"^(draft|sent|accepted|rejected|completed|hired)$", description="New proposal status (valid transitions depend on user role)")
    message: Optional[str] = Field(None, description="Updated cover message (company only, draft proposals only)")
    budget_range: Optional[str] = Field(None, max_length=100, description="Updated budget range (company only, draft proposals only)")
    hiring_notes: Optional[str] = Field(None, description="Notes added when hiring the talent")


class ProposalResponse(BaseModel):
    id: str = Field(description="Unique proposal identifier")
    company_id: str = Field(description="Company that created the proposal")
    company_name: str = Field(description="Display name of the company")
    talent_id: str = Field(description="Talent who received the proposal")
    talent_name: str = Field(description="Display name of the talent")
    status: str = Field(description="Current status (draft, sent, accepted, rejected, completed, hired)")
    message: Optional[str] = Field(None, description="Cover message from the company")
    budget_range: Optional[str] = Field(None, description="Budget range for the training")
    courses: list[ProposalCourseResponse] = Field(default_factory=list, description="Ordered list of courses in the learning path")
    progress: float = Field(0.0, description="Completion progress from 0.0 to 1.0")
    total_xp: int = Field(0, description="Total experience points accumulated")
    milestones: list[MilestoneResponse] = Field(default_factory=list, description="Achievements unlocked during the learning path")
    hired_at: Optional[datetime] = Field(None, description="Timestamp when the talent was hired")
    hiring_notes: Optional[str] = Field(None, description="Notes from the hiring decision")
    created_at: datetime = Field(description="Proposal creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")


class ProposalListResponse(BaseModel):
    items: list[ProposalResponse] = Field(description="List of proposals for the current page")
    total: int = Field(description="Total number of matching proposals")
    page: int = Field(description="Current page number (1-based)")
    page_size: int = Field(description="Number of items per page")


class CourseNotesUpdate(BaseModel):
    talent_notes: Optional[str] = Field(None, description="Talent's personal notes or reflections on the course")


class CompanyCourseUpdate(BaseModel):
    company_notes: Optional[str] = Field(None, description="Company's notes or instructions for the talent")
    deadline: Optional[datetime] = Field(None, description="Deadline for course completion (ISO 8601 datetime)")
