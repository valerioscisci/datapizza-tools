from __future__ import annotations

from typing import Literal, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from api.database.connection import get_db
from api.database.models import News
from api.routes.news.schemas import NewsResponse, NewsListResponse
from api.utils import safe_parse_json_list

router = APIRouter(prefix="/news", tags=["News"])


def _to_news_response(news: News) -> NewsResponse:
    return NewsResponse(
        id=news.id,
        title=news.title,
        summary=news.summary,
        source=news.source,
        source_url=news.source_url,
        category=news.category,
        tags=safe_parse_json_list(news.tags_json),
        author=news.author,
        published_at=news.published_at,
        created_at=news.created_at,
        updated_at=news.updated_at,
    )


@router.get("", response_model=NewsListResponse)
async def list_news(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    category: Optional[Literal["AI", "tech", "careers"]] = None,
    db: Session = Depends(get_db),
):
    """List all active news items with pagination."""
    query = db.query(News).filter(News.is_active == 1)

    if category:
        query = query.filter(News.category == category)

    total = query.count()
    news_items = query.order_by(News.published_at.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()

    return NewsListResponse(
        items=[_to_news_response(n) for n in news_items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{news_id}", response_model=NewsResponse)
async def get_news(
    news_id: str,
    db: Session = Depends(get_db),
):
    """Get a single news item by ID."""
    news = db.query(News).filter(News.id == news_id, News.is_active == 1).first()

    if not news:
        raise HTTPException(status_code=404, detail="News not found")

    return _to_news_response(news)
