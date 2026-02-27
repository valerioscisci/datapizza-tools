"""Custom OpenAPI schema configuration for Datapizza Tools API.

Centralizes tag metadata, security schemes, and API documentation.
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi


TAGS_METADATA = [
    {
        "name": "Auth",
        "description": "Authentication endpoints for user signup, login, and session management. Supports talent and company account types with JWT-based authentication.",
    },
    {
        "name": "Jobs",
        "description": "Job listings from the Datapizza platform. Browse active positions with filters for work mode, pagination, and more.",
    },
    {
        "name": "Applications",
        "description": "Job application management. Talents can apply to jobs, track application status, and view their application history.",
    },
    {
        "name": "News",
        "description": "Tech news and articles aggregated by Datapizza. Browse by category with pagination support.",
    },
    {
        "name": "Courses",
        "description": "Training courses catalog. Browse courses by category and level, with details on providers, pricing, and ratings.",
    },
    {
        "name": "Profile",
        "description": "User profile management. View and update personal info, skills, availability, and professional details.",
    },
    {
        "name": "Profile - Experiences",
        "description": "Work experience management within the user profile. Add, update, and remove professional experiences.",
    },
    {
        "name": "Profile - Educations",
        "description": "Education history management within the user profile. Add, update, and remove education entries.",
    },
    {
        "name": "Profile - AI Readiness",
        "description": "AI Agent Readiness self-assessment quiz. Take the quiz to measure AI-readiness across 8 dimensions, view results, and get personalized course suggestions for weak areas.",
    },
    {
        "name": "Talents",
        "description": "Public talent directory for companies. Browse and search available developers by skills, experience, location, and availability.",
    },
    {
        "name": "Proposals",
        "description": "Craft Your Developer proposal management. Companies create training proposals for talents with course selections, budget, and milestones. Supports the full lifecycle: draft, sent, accepted, in-progress, completed, hired.",
    },
    {
        "name": "Proposals - Messages",
        "description": "Messaging within a proposal. Companies and talents can exchange messages during the training program.",
    },
    {
        "name": "AI",
        "description": "AI-powered features using Google Gemini. Includes job matching with profile-based scoring, career advice with personalized recommendations, skill gap analysis with market demand classification, and market trend monitoring.",
    },
    {
        "name": "Notifications",
        "description": "Email notification center and preferences. View emails, manage read status, configure notification channels (email, Telegram), and trigger daily digest.",
    },
    {
        "name": "Health",
        "description": "API health check endpoint.",
    },
]


def custom_openapi(app: FastAPI) -> dict:
    """Generate a custom OpenAPI schema with enhanced documentation."""
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="Datapizza Tools API",
        version="0.1.0",
        summary="Platform API for Datapizza Tools — job matching, training programs, and talent management",
        description="""
## Overview

Datapizza Tools is a platform that connects companies with tech talent through AI-powered job matching
and the **Craft Your Developer** training program.

## Main Features

- **Job Board** — Browse and apply to tech job listings
- **Craft Your Developer** — Companies propose personalized training programs for talents, with course delivery, milestone tracking, gamification (XP system), and hiring flow
- **AI Career Advisor** — Gemini-powered job matching and career recommendations
- **Talent Directory** — Companies browse public developer profiles

## Authentication

Most endpoints require a JWT Bearer token obtained via `/api/v1/auth/login` or `/api/v1/auth/signup`.
Include the token in the `Authorization` header: `Bearer <token>`.

## Account Types

- **talent** — Developers looking for jobs and training opportunities
- **company** — Companies posting jobs and creating training proposals
""",
        routes=app.routes,
        tags=TAGS_METADATA,
    )

    # Security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "JWT access token obtained from /api/v1/auth/login or /api/v1/auth/signup",
        }
    }

    # Apply security globally
    openapi_schema["security"] = [{"BearerAuth": []}]

    # Contact info
    openapi_schema["info"]["contact"] = {
        "name": "Datapizza",
        "url": "https://www.datapizza.tech",
    }

    # Servers
    openapi_schema["servers"] = [
        {"url": "http://localhost:8003", "description": "Local development server"},
    ]

    app.openapi_schema = openapi_schema
    return openapi_schema
