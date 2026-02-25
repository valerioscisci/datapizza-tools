from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class NewsResponse(BaseModel):
    id: str = Field(..., description="Unique news article identifier")
    title: str = Field(..., description="Article headline")
    summary: str = Field(..., description="Short article summary")
    source: str = Field(..., description="News source name")
    source_url: Optional[str] = Field(None, description="Link to original article")
    category: str = Field(..., description="Category: AI, tech, or careers")
    tags: list[str] = Field(default_factory=list, description="Topic tags")
    author: Optional[str] = None
    published_at: datetime = Field(..., description="Original publication date")
    created_at: datetime = Field(..., description="Record creation timestamp")
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class NewsListResponse(BaseModel):
    items: list[NewsResponse] = Field(..., description="List of news articles")
    total: int = Field(..., description="Total number of matching articles")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
