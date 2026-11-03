"""
Cache service — encapsulates TTL check and upsert logic for GitHub data.

Cache TTLs (configurable via .env):
  Profile / Repositories  → 1 hour
  Contributions           → 6 hours
  Settings / Featured     → no expiry
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.config import settings
from app.models.models import (
    Contribution, FeaturedRepository, Repository, User, UserSettings,
)
from app.services import github_service
from app.utils.helpers import is_fresh, utcnow

logger = logging.getLogger(__name__)


# ─── Cache freshness checks ─────────────────────────────────────────────


def profile_is_fresh(user: User) -> bool:
    return is_fresh(user.last_synced_at, settings.profile_cache_ttl)


def contributions_are_fresh(user: User, db: Session) -> bool:
    latest = (
        db.query(Contribution)
        .filter(Contribution.user_id == user.id)
        .order_by(Contribution.cached_at.desc())
        .first()
    )
    if not latest:
        return False
    return is_fresh(latest.cached_at, settings.contribution_cache_ttl)


# ─── User upsert ────────────────────────────────────────────────────────


def upsert_user(db: Session, profile_data: Dict[str, Any]) -> User:
    """Insert or update a user row from normalized GitHub profile data."""
    username = profile_data["github_username"]
    user = db.query(User).filter(User.github_username == username).first()
    now = utcnow()

    if user is None:
        user = User(
            created_at=now,
            updated_at=now,
            last_synced_at=now,
            **profile_data,
        )
        db.add(user)
    else:
        for key, value in profile_data.items():
            setattr(user, key, value)
        user.updated_at = now
        user.last_synced_at = now

    db.flush()
    return user


# ─── Repository upsert ──────────────────────────────────────────────────


def upsert_repositories(
    db: Session, user: User, repo_data_list: List[Dict[str, Any]]
) -> List[Repository]:
    """Upsert all repositories for a user and recompute total_stars and total_forks."""
    now = utcnow()
    results: List[Repository] = []
    seen_ids = set()

    for data in repo_data_list:
        github_repo_id = data["github_repo_id"]
        seen_ids.add(github_repo_id)

        repo = (
            db.query(Repository)
            .filter(Repository.github_repo_id == github_repo_id)
            .first()
        )

        if repo is None:
            repo = Repository(user_id=user.id, cached_at=now, **data)
            db.add(repo)
        else:
            for key, val in data.items():
                setattr(repo, key, val)
            repo.cached_at = now

        results.append(repo)

    db.flush()

    # Recompute totals directly from stored repos
    total_stars = sum(r.stars for r in results)
    total_forks = sum(r.forks for r in results)
    user.total_stars = total_stars
    user.total_forks = total_forks
    db.flush()

    return results


# ─── Contribution upsert ─────────────────────────────────────────────────


def upsert_contributions(
    db: Session, user: User, calendar_data: Dict[str, Any]
) -> int:
    """Upsert daily contribution records from GraphQL calendar data."""
    now = utcnow()
    count = 0

    weeks = calendar_data.get("weeks", [])
    for week in weeks:
        for day in week.get("contributionDays", []):
            date_str = day["date"]
            contribution_count = day.get("contributionCount", 0)

            existing = (
                db.query(Contribution)
                .filter(
                    Contribution.user_id == user.id,
                    Contribution.contribution_date == date_str,
                )
                .first()
            )

            if existing is None:
                record = Contribution(
                    user_id=user.id,
                    contribution_date=date_str,
                    contribution_count=contribution_count,
                    cached_at=now,
                )
                db.add(record)
            else:
                existing.contribution_count = contribution_count
                existing.cached_at = now

            count += 1

    db.flush()
    return count


# ─── Full sync orchestration ─────────────────────────────────────────────


async def sync_profile(
    db: Session, username: str, force_refresh: bool = False
) -> tuple[User, str]:
    """
    Fetch and store GitHub profile + repositories.
    Returns (user, cache_status) where cache_status is 'hit', 'miss', or 'stale'.
    """
    user = db.query(User).filter(User.github_username == username).first()

    if user and profile_is_fresh(user) and not force_refresh:
        return user, "hit"

    cache_status = "miss" if not user else "refresh"
    stale_user = user  # keep reference so we can return stale data on failure

    try:
        raw_profile = await github_service.fetch_github_profile(username)
        normalized = github_service.normalize_profile(raw_profile)
        user = upsert_user(db, normalized)

        raw_repos = await github_service.fetch_github_repositories(username)
        normalized_repos = [github_service.normalize_repository(r) for r in raw_repos]
        upsert_repositories(db, user, normalized_repos)

        db.commit()
        db.refresh(user)
        return user, cache_status

    except Exception as exc:
        db.rollback()
        logger.error("GitHub sync failed for %s: %s", username, exc)
        if stale_user:
            return stale_user, "stale"
        raise


async def sync_contributions(db: Session, user: User, force_refresh: bool = False) -> bool:
    """
    Fetch and store contribution calendar.
    Returns True if data was fetched, False if unavailable/cached.
    """
    if not force_refresh and contributions_are_fresh(user, db):
        return True

    calendar_data = await github_service.fetch_contributions(user.github_username)
    if calendar_data is None:
        return False

    upsert_contributions(db, user, calendar_data)
    db.commit()
    return True


# ─── Settings helpers ────────────────────────────────────────────────────


def get_or_create_settings(db: Session, user: User) -> UserSettings:
    settings_obj = db.query(UserSettings).filter(UserSettings.user_id == user.id).first()
    if not settings_obj:
        settings_obj = UserSettings(user_id=user.id, theme="light", created_at=utcnow(), updated_at=utcnow())
        db.add(settings_obj)
        db.flush()
    return settings_obj
