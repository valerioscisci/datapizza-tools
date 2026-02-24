from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class CourseResponse(BaseModel):
    id: str
    title: str
    description: str
    provider: str
    url: str
    instructor: Optional[str] = None
    level: str
    duration: Optional[str] = None
    price: Optional[str] = None
    rating: Optional[str] = None
    students_count: Optional[int] = None
    category: str
    tags: list[str] = Field(default_factory=list)
    image_url: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CourseListResponse(BaseModel):
    items: list[CourseResponse]
    total: int
    page: int
    page_size: int
