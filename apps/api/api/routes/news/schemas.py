from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class NewsResponse(BaseModel):
    id: str
    title: str
    summary: str
    source: str
    source_url: Optional[str] = None
    category: str
    tags: list[str] = Field(default_factory=list)
    author: Optional[str] = None
    published_at: datetime
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class NewsListResponse(BaseModel):
    items: list[NewsResponse]
    total: int
    page: int
    page_size: int
