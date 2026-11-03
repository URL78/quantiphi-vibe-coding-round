"""Central API router — mounts all endpoint routers under /api/v1."""

from fastapi import APIRouter
from app.api.endpoints import (
    analytics,
    career,
    compatibility,
    contributions,
    deepwiki,
    interview,
    portfolio,
    profile,
    repositories,
    settings,
)

api_router = APIRouter()

api_router.include_router(profile.router)
api_router.include_router(analytics.router)
api_router.include_router(contributions.router)
api_router.include_router(repositories.router)
api_router.include_router(compatibility.router)
api_router.include_router(career.router)
api_router.include_router(deepwiki.router)
api_router.include_router(interview.router)
api_router.include_router(settings.router)
api_router.include_router(portfolio.router)
