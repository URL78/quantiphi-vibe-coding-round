"""Shared utility helpers."""

from datetime import datetime, timezone
from typing import Optional


def utcnow() -> datetime:
    """Return current UTC time (timezone-aware)."""
    return datetime.now(timezone.utc)


def seconds_since(dt: Optional[datetime]) -> Optional[float]:
    """Return seconds elapsed since dt (UTC). None if dt is None."""
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return (utcnow() - dt).total_seconds()


def is_fresh(dt: Optional[datetime], ttl_seconds: int) -> bool:
    """Return True if dt is within TTL window."""
    age = seconds_since(dt)
    if age is None:
        return False
    return age < ttl_seconds


def sanitize_username(username: str) -> str:
    """Strip whitespace and basic validation for GitHub usernames."""
    username = username.strip()
    if not username:
        raise ValueError("Username cannot be empty.")
    if len(username) > 100:
        raise ValueError("Username is too long.")
    return username


def intensity_from_count(count: int) -> int:
    """Convert a contribution count to a 0–4 intensity level (like GitHub's heatmap)."""
    if count == 0:
        return 0
    elif count <= 3:
        return 1
    elif count <= 6:
        return 2
    elif count <= 9:
        return 3
    else:
        return 4
