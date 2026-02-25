from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class CourseResponse(BaseModel):
    id: str = Field(..., description="Unique course identifier")
    title: str = Field(..., description="Course title")
    description: str = Field(..., description="Course description")
    provider: str = Field(..., description="Course provider (e.g. Udemy, Coursera)")
    url: str = Field(..., description="Link to the course page")
    instructor: Optional[str] = Field(None, description="Course instructor name")
    level: str = Field(..., description="Difficulty level: beginner, intermediate, advanced")
    duration: Optional[str] = Field(None, description="Estimated course duration")
    price: Optional[str] = Field(None, description="Course price")
    rating: Optional[str] = Field(None, description="Average rating")
    students_count: Optional[int] = Field(None, description="Number of enrolled students")
    category: str = Field(..., description="Category: AI, ML, frontend, backend, devops")
    tags: list[str] = Field(default_factory=list, description="Topic tags")
    image_url: Optional[str] = Field(None, description="Course thumbnail URL")
    created_at: datetime = Field(..., description="Record creation timestamp")
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CourseListResponse(BaseModel):
    items: list[CourseResponse] = Field(..., description="List of courses")
    total: int = Field(..., description="Total number of matching courses")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
