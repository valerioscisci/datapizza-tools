from __future__ import annotations

from pydantic import BaseModel, Field
from datetime import datetime


class MessageCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=2000, description="Message text (1-2000 characters)")


class MessageResponse(BaseModel):
    id: str = Field(description="Unique message identifier")
    sender_id: str = Field(description="User ID of the sender")
    sender_name: str = Field(description="Display name of the sender")
    sender_type: str = Field(description="Sender role: 'company' or 'talent'")
    content: str = Field(description="Message text content")
    created_at: datetime = Field(description="When the message was sent")


class MessageListResponse(BaseModel):
    items: list[MessageResponse] = Field(description="List of messages for the current page")
    total: int = Field(description="Total number of messages in this proposal")
    page: int = Field(description="Current page number (1-based)")
    page_size: int = Field(description="Number of items per page")
