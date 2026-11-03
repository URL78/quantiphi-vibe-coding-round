"""Analytics endpoints — aggregate stats and language distribution."""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import User
from app.schemas.schemas import AnalyticsResponse, LanguageStat, LanguagesResponse
from app.services.analytics_service import get_language_distribution, get_total_contributions
from app.utils.helpers import is_fresh
from app.config import settings

router = APIRouter(tags=["Analytics"])
logger = logging.getLogger(__name__)


def _get_user_or_404(username: str, db: Session) -> User:
    user = db.query(User).filter(User.github_username == username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "USER_NOT_FOUND", "message": f"No cached profile for '{username}'. Please sync first."},
        )
    return user


@router.get("/analytics/{username}", response_model=AnalyticsResponse)
async def get_analytics(username: str, db: Session = Depends(get_db)):
    """Return aggregate profile statistics."""
    user = _get_user_or_404(username, db)
    total_contributions = get_total_contributions(db, user)
    is_stale = not is_fresh(user.last_synced_at, settings.profile_cache_ttl)

    return AnalyticsResponse(
        username=user.github_username,
        followers=user.followers,
        following=user.following,
        public_repos=user.public_repos,
        total_stars=user.total_stars,
        total_forks=user.total_forks,
        total_contributions=total_contributions,
        is_stale=is_stale,
    )


@router.get("/analytics/{username}/languages", response_model=LanguagesResponse)
async def get_languages(username: str, db: Session = Depends(get_db)):
    """Return primary-language distribution across cached repositories."""
    user = _get_user_or_404(username, db)
    distribution = get_language_distribution(db, user)

    return LanguagesResponse(
        username=user.github_username,
        basis="repository_count",
        languages=[LanguageStat(**item) for item in distribution],
    )
