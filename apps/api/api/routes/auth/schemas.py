from __future__ import annotations

import re
from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional
from datetime import datetime

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


def _normalize_email(v: str) -> str:
    v = v.strip().lower()
    if not EMAIL_REGEX.match(v):
        raise ValueError("Invalid email format")
    return v


class SignupRequest(BaseModel):
    email: str = Field(..., min_length=1, max_length=255, description="User email address (must be unique)")
    password: str = Field(..., min_length=6, max_length=255, description="Password (minimum 6 characters)")
    full_name: str = Field(..., min_length=1, max_length=255, description="User full name")
    user_type: str = Field("talent", pattern=r"^(talent|company)$", description="Account type: 'talent' or 'company'")
    company_name: Optional[str] = Field(None, min_length=1, max_length=255, description="Required when user_type is 'company'")
    company_website: Optional[str] = Field(None, max_length=500, description="Company website URL")
    industry: Optional[str] = Field(None, max_length=255, description="Industry sector")

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        return _normalize_email(v)

    @model_validator(mode="after")
    def validate_company_name(self):
        if self.user_type == "company" and not self.company_name:
            raise ValueError("company_name is required when user_type is 'company'")
        return self


class LoginRequest(BaseModel):
    email: str = Field(..., min_length=1, max_length=255, description="Registered email address")
    password: str = Field(..., min_length=1, max_length=255, description="Account password")

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        return _normalize_email(v)


class TokenResponse(BaseModel):
    access_token: str = Field(..., description="JWT bearer token")
    token_type: str = Field("bearer", description="Token type (always 'bearer')")


class UserResponse(BaseModel):
    id: str = Field(..., description="Unique user identifier")
    email: str = Field(..., description="User email address")
    full_name: str = Field(..., description="User full name")
    phone: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    experience_level: Optional[str] = Field(None, description="e.g. junior, mid, senior")
    experience_years: Optional[str] = None
    current_role: Optional[str] = None
    skills: list[str] = Field(default_factory=list, description="List of skill tags")
    availability_status: str = Field("available", description="Job availability status")
    reskilling_status: Optional[str] = None
    adopted_by_company: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    user_type: str = Field("talent", description="Account type: 'talent' or 'company'")
    company_name: Optional[str] = None
    company_website: Optional[str] = None
    company_size: Optional[str] = None
    industry: Optional[str] = None
    created_at: datetime = Field(..., description="Account creation timestamp")
