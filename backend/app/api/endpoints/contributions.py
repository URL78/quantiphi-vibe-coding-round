"""Contribution endpoints — heatmap calendar and streaks."""

import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import User
from app.schemas.schemas import ContributionDay, ContributionsResponse, StreakResponse
from app.services.analytics_service import (
    calculate_streaks,
    get_contribution_calendar,
    get_total_contributions,
)
from app.services.cache_service import sync_contributions
from app.utils.helpers import is_fresh
from app.config import settings

router = APIRouter(tags=["Contributions"])
logger = logging.getLogger(__name__)


def _get_user_or_404(username: str, db: Session) -> User:
    user = db.query(User).filter(User.github_username == username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "USER_NOT_FOUND", "message": f"No cached profile for '{username}'. Please sync first."},
        )
    return user


@router.get("/contributions/{username}", response_model=ContributionsResponse)
async def get_contributions(
    username: str,
    from_date: Optional[str] = Query(None, alias="from"),
    to_date: Optional[str] = Query(None, alias="to"),
    db: Session = Depends(get_db),
):
    """Return daily contribution calendar data (fetches from GitHub if stale)."""
    user = _get_user_or_404(username, db)

    # Try to sync contributions if stale
    await sync_contributions(db, user)

    contributions = get_contribution_calendar(db, user, from_date, to_date)
    total = get_total_contributions(db, user)
    is_stale = not is_fresh(user.last_synced_at, settings.contribution_cache_ttl)

    return ContributionsResponse(
        username=user.github_username,
        total_contributions=total,
        contributions=[ContributionDay(**c) for c in contributions],
        is_stale=is_stale,
    )


@router.get("/contributions/{username}/streaks", response_model=StreakResponse)
async def get_streaks(username: str, db: Session = Depends(get_db)):
    """Return current and longest contribution streaks."""
    user = _get_user_or_404(username, db)

    # Try to sync contributions if stale
    await sync_contributions(db, user)

    streak_data = calculate_streaks(db, user)

    return StreakResponse(
        username=user.github_username,
        current_streak=streak_data["current_streak"],
        longest_streak=streak_data["longest_streak"],
        last_contribution_date=streak_data["last_contribution_date"],
    )
