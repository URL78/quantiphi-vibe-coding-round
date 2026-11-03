"""Settings endpoints — get and update user theme preferences."""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import User
from app.schemas.schemas import SettingsResponse, SettingsUpdateRequest
from app.services.cache_service import get_or_create_settings
from app.utils.helpers import utcnow

router = APIRouter(prefix="/settings", tags=["Settings"])
logger = logging.getLogger(__name__)


def _get_user_or_404(username: str, db: Session) -> User:
    user = db.query(User).filter(User.github_username == username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "USER_NOT_FOUND", "message": f"No cached profile for '{username}'."},
        )
    return user


@router.get("/{username}", response_model=SettingsResponse)
async def get_settings(username: str, db: Session = Depends(get_db)):
    """Return user dashboard settings."""
    user = _get_user_or_404(username, db)
    settings_obj = get_or_create_settings(db, user)
    db.commit()
    return SettingsResponse(username=user.github_username, theme=settings_obj.theme)


@router.put("/{username}", response_model=SettingsResponse)
async def update_settings(
    username: str, payload: SettingsUpdateRequest, db: Session = Depends(get_db)
):
    """Update user dashboard settings."""
    user = _get_user_or_404(username, db)
    settings_obj = get_or_create_settings(db, user)
    settings_obj.theme = payload.theme
    settings_obj.updated_at = utcnow()
    db.commit()
    return SettingsResponse(username=user.github_username, theme=settings_obj.theme)
