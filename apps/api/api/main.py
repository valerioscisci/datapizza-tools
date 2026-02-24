from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.database.connection import engine, Base
from api.routes import jobs, auth, applications, news, courses, profile, talents, proposals

app = FastAPI(
    title="Datapizza Tools API",
    description="API for the Datapizza Tools platform",
    version="0.1.0",
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
app.include_router(jobs.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")
app.include_router(applications.router, prefix="/api/v1")
app.include_router(news.router, prefix="/api/v1")
app.include_router(courses.router, prefix="/api/v1")
app.include_router(profile.router, prefix="/api/v1")
app.include_router(talents.router, prefix="/api/v1")
app.include_router(proposals.router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    return {"status": "ok"}
