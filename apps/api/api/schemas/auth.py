from __future__ import annotations

import re
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


def _normalize_email(v: str) -> str:
    v = v.strip().lower()
    if not EMAIL_REGEX.match(v):
        raise ValueError("Invalid email format")
    return v


class SignupRequest(BaseModel):
    email: str = Field(..., min_length=1, max_length=255)
    password: str = Field(..., min_length=6, max_length=255)
    full_name: str = Field(..., min_length=1, max_length=255)

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        return _normalize_email(v)


class LoginRequest(BaseModel):
    email: str = Field(..., min_length=1, max_length=255)
    password: str = Field(..., min_length=1, max_length=255)

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        return _normalize_email(v)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    phone: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    experience_level: Optional[str] = None
    experience_years: Optional[str] = None
    current_role: Optional[str] = None
    skills: list[str] = Field(default_factory=list)
    availability_status: str = "available"
    reskilling_status: Optional[str] = None
    adopted_by_company: Optional[str] = None
    created_at: datetime
