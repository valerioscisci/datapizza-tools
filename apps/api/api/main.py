from __future__ import annotations

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.database.connection import engine, Base
from api.openapi import TAGS_METADATA, custom_openapi
from api.routes.jobs import router as jobs_router
from api.routes.auth import router as auth_router
from api.routes.applications import router as applications_router
from api.routes.news import router as news_router
from api.routes.courses import router as courses_router
from api.routes.profile import router as profile_router
from api.routes.talents import router as talents_router
from api.routes.proposals import router as proposals_router
from api.routes.ai import router as ai_router

app = FastAPI(
    title="Datapizza Tools API",
    description="API for the Datapizza Tools platform",
    version="0.1.0",
    openapi_tags=TAGS_METADATA,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3003"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables
Base.metadata.create_all(bind=engine)

# Include routes
app.include_router(jobs_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
app.include_router(applications_router, prefix="/api/v1")
app.include_router(news_router, prefix="/api/v1")
app.include_router(courses_router, prefix="/api/v1")
app.include_router(profile_router, prefix="/api/v1")
app.include_router(talents_router, prefix="/api/v1")
app.include_router(proposals_router, prefix="/api/v1")
app.include_router(ai_router, prefix="/api/v1")

app.openapi = lambda: custom_openapi(app)


@app.get(
    "/health",
    tags=["Health"],
    summary="Health check",
    description="Returns API health status. No authentication required.",
    responses={200: {"description": "API is healthy", "content": {"application/json": {"example": {"status": "ok"}}}}},
)
async def health_check():
    """Check if the API is running and healthy."""
    return {"status": "ok"}
