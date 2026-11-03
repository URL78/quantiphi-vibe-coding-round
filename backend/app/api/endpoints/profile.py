"""Profile endpoints — sync, get, refresh."""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import User
from app.schemas.schemas import ProfileResponse, ProfileSyncRequest, ProfileSyncResponse
from app.services import cache_service
from app.utils.helpers import is_fresh, sanitize_username
from app.config import settings

router = APIRouter(prefix="/profile", tags=["Profile"])
logger = logging.getLogger(__name__)


def _get_user_or_404(username: str, db: Session) -> User:
    user = db.query(User).filter(User.github_username == username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "USER_NOT_FOUND", "message": f"No cached profile for '{username}'. Please sync first."},
        )
    return user


@router.post("/sync", response_model=ProfileSyncResponse, status_code=status.HTTP_200_OK)
async def sync_profile(request: ProfileSyncRequest, db: Session = Depends(get_db)):
    """Synchronize a public GitHub profile and its repositories."""
    username = sanitize_username(request.username)
    try:
        user, cache_status = await cache_service.sync_profile(
            db, username, force_refresh=request.force_refresh
        )
        return ProfileSyncResponse(
            success=True,
            username=user.github_username,
            message=f"Profile {'refreshed' if request.force_refresh else 'synchronized'} successfully.",
            cache_status=cache_status,
            last_synced_at=user.last_synced_at,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "GITHUB_USER_NOT_FOUND", "message": str(exc)},
        )
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"code": "GITHUB_UNAVAILABLE", "message": str(exc)},
        )


@router.get("/{username}", response_model=ProfileResponse)
async def get_profile(username: str, db: Session = Depends(get_db)):
    """Return cached profile details."""
    user = _get_user_or_404(username, db)
    is_stale = not is_fresh(user.last_synced_at, settings.profile_cache_ttl)

    # Count featured repo ids for the response
    from app.models.models import FeaturedRepository
    featured_ids = {
        fr.repository_id
        for fr in db.query(FeaturedRepository).filter(FeaturedRepository.user_id == user.id).all()
    }

    return ProfileResponse(
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
        is_stale=is_stale,
    )


@router.post("/{username}/refresh", response_model=ProfileSyncResponse)
async def refresh_profile(username: str, db: Session = Depends(get_db)):
    """Force-refresh profile and repository data."""
    username = sanitize_username(username)
    try:
        user, cache_status = await cache_service.sync_profile(db, username, force_refresh=True)
        return ProfileSyncResponse(
            success=True,
            username=user.github_username,
            message="Profile refreshed successfully.",
            cache_status=cache_status,
            last_synced_at=user.last_synced_at,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "GITHUB_USER_NOT_FOUND", "message": str(exc)},
        )
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"code": "GITHUB_UNAVAILABLE", "message": str(exc)},
        )
