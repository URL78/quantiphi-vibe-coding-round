"""Portfolio endpoint — public composed portfolio view."""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import User
from app.schemas.schemas import (
    AnalyticsResponse, CompatibilityResponse, LanguageStat,
    PortfolioResponse, ProfileResponse, RepositoryOut,
)
from app.services.portfolio_service import get_portfolio

router = APIRouter(prefix="/portfolio", tags=["Portfolio"])
logger = logging.getLogger(__name__)


@router.get("/{username}", response_model=PortfolioResponse)
async def get_portfolio_view(username: str, db: Session = Depends(get_db)):
    """Return a composed public portfolio for a GitHub username."""
    user = db.query(User).filter(User.github_username == username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "USER_NOT_FOUND", "message": f"No cached profile for '{username}'."},
        )

    data = get_portfolio(db, user)
    featured_ids = data["featured_ids"]

    # Build featured repos list
    featured_repos_out = [
        RepositoryOut(
            **{c.name: getattr(repo, c.name) for c in repo.__table__.columns},
            featured=True,
        )
        for repo in data["featured_repositories"]
    ]

    # Build latest analysis if exists
    latest_analysis = None
    if data["latest_analysis"]:
        a = data["latest_analysis"]
        latest_analysis = CompatibilityResponse(
            analysis_id=a.id,
            username=user.github_username,
            match_percentage=a.match_percentage,
            recognized_required_languages=a.recognized_required_languages or [],
            matched_languages=a.matched_languages or [],
            unmatched_languages=a.unmatched_languages or [],
            unassessed_keywords=a.unassessed_keywords or [],
            score_basis=a.score_basis,
            message="GitHub evidence-based compatibility estimate.",
        )

    return PortfolioResponse(
        profile=ProfileResponse(
            id=user.id,
            github_username=user.github_username,
            name=user.name,
            bio=user.bio,
            avatar_url=user.avatar_url,
            github_url=user.github_url,
            followers=user.followers,
            following=user.following,
            public_repos=user.public_repos,
            total_stars=user.total_stars,
            total_forks=user.total_forks,
            last_synced_at=user.last_synced_at,
            is_stale=False,
        ),
        analytics=AnalyticsResponse(**data["analytics"]),
        languages=[LanguageStat(**lang) for lang in data["languages"]],
        featured_repositories=featured_repos_out,
        latest_analysis=latest_analysis,
    )
