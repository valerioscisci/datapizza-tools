from __future__ import annotations

from typing import Literal, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from api.database.connection import get_db
from api.database.models import Course
from api.routes.courses.schemas import CourseResponse, CourseListResponse
from api.utils import safe_parse_json_list

router = APIRouter(prefix="/courses", tags=["Courses"])


def _to_course_response(course: Course) -> CourseResponse:
    return CourseResponse(
        id=course.id,
        title=course.title,
        description=course.description,
        provider=course.provider,
        url=course.url,
        instructor=course.instructor,
        level=course.level,
        duration=course.duration,
        price=course.price,
        rating=course.rating,
        students_count=course.students_count,
        category=course.category,
        tags=safe_parse_json_list(course.tags_json),
        image_url=course.image_url,
        created_at=course.created_at,
        updated_at=course.updated_at,
    )


@router.get("", response_model=CourseListResponse)
async def list_courses(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    category: Optional[Literal["AI", "ML", "frontend", "backend", "devops"]] = None,
    level: Optional[Literal["beginner", "intermediate", "advanced"]] = None,
    db: Session = Depends(get_db),
):
    """List all active courses with pagination."""
    query = db.query(Course).filter(Course.is_active == 1)

    if category:
        query = query.filter(Course.category == category)

    if level:
        query = query.filter(Course.level == level)

    total = query.count()
    courses = query.order_by(Course.created_at.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()

    return CourseListResponse(
        items=[_to_course_response(c) for c in courses],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{course_id}", response_model=CourseResponse)
async def get_course(
    course_id: str,
    db: Session = Depends(get_db),
):
    """Get a single course by ID."""
    course = db.query(Course).filter(Course.id == course_id, Course.is_active == 1).first()

    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    return _to_course_response(course)
