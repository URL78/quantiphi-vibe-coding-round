"""
Analytics service — language distribution, contribution streaks.

All business-critical calculations run on the backend, never the frontend.
"""

import logging
from datetime import date, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.models.models import Contribution, Repository, User
from app.utils.helpers import intensity_from_count

logger = logging.getLogger(__name__)


# ─── Language distribution ───────────────────────────────────────────────


def get_language_distribution(db: Session, user: User) -> List[Dict[str, Any]]:
    """
    Aggregate repos by primary language.
    Returns a sorted list of {name, repository_count, percentage}.
    Repos without a detected language are excluded from the denominator.
    """
    repos = (
        db.query(Repository)
        .filter(Repository.user_id == user.id, Repository.language.isnot(None))
        .all()
    )

    language_counts: Dict[str, int] = {}
    for repo in repos:
        lang = repo.language.strip()
        if lang:
            language_counts[lang] = language_counts.get(lang, 0) + 1

    total = sum(language_counts.values())
    if total == 0:
        return []

    distribution = [
        {
            "name": lang,
            "repository_count": count,
            "percentage": round((count / total) * 100, 1),
        }
        for lang, count in language_counts.items()
    ]

    return sorted(distribution, key=lambda x: x["repository_count"], reverse=True)


# ─── Contribution streak calculation ─────────────────────────────────────


def calculate_streaks(db: Session, user: User) -> Dict[str, Any]:
    """
    Calculate current and longest contribution streaks from stored daily records.

    Streak definition: consecutive calendar days with contribution_count > 0.
    A zero-contribution day breaks the streak.
    Current streak counts backwards from today; if the most recent contribution
    was yesterday, the streak is still considered active.
    """
    records = (
        db.query(Contribution)
        .filter(Contribution.user_id == user.id, Contribution.contribution_count > 0)
        .order_by(Contribution.contribution_date.asc())
        .all()
    )

    if not records:
        return {
            "current_streak": 0,
            "longest_streak": 0,
            "last_contribution_date": None,
        }

    # Build a set of active dates (ISO string → date obj)
    active_dates = {date.fromisoformat(r.contribution_date) for r in records}
    last_contribution_date = max(active_dates)

    # Longest streak — scan forward
    sorted_dates = sorted(active_dates)
    longest = 1
    current_run = 1
    for i in range(1, len(sorted_dates)):
        if (sorted_dates[i] - sorted_dates[i - 1]).days == 1:
            current_run += 1
            longest = max(longest, current_run)
        else:
            current_run = 1

    # Current streak — count backwards from today (or yesterday if today is empty)
    today = date.today()
    anchor = today if today in active_dates else today - timedelta(days=1)

    current_streak = 0
    cursor = anchor
    while cursor in active_dates:
        current_streak += 1
        cursor -= timedelta(days=1)

    return {
        "current_streak": current_streak,
        "longest_streak": longest,
        "last_contribution_date": last_contribution_date.isoformat(),
    }


# ─── Contribution calendar (for heatmap) ─────────────────────────────────


def get_contribution_calendar(
    db: Session,
    user: User,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Return daily contribution records formatted for the heatmap component."""
    query = db.query(Contribution).filter(Contribution.user_id == user.id)

    if from_date:
        query = query.filter(Contribution.contribution_date >= from_date)
    if to_date:
        query = query.filter(Contribution.contribution_date <= to_date)

    records = query.order_by(Contribution.contribution_date.asc()).all()

    return [
        {
            "date": r.contribution_date,
            "count": r.contribution_count,
            "intensity": intensity_from_count(r.contribution_count),
        }
        for r in records
    ]


def get_total_contributions(db: Session, user: User) -> int:
    """Sum all stored contribution counts."""
    rows = db.query(Contribution).filter(Contribution.user_id == user.id).all()
    return sum(r.contribution_count for r in rows)
