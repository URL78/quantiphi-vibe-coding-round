"""Vibe Check / Tech Stack Compatibility endpoints (MANDATORY).

Auto-syncs the GitHub profile if not cached yet, so the user
never has to manually sync before running a Vibe Check.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import CompatibilityAnalysis, User
from app.schemas.schemas import CompatibilityRequest, CompatibilityResponse
from app.services.cache_service import sync_profile
from app.services.compatibility_service import analyze_compatibility

router = APIRouter(prefix="/compatibility", tags=["Vibe Check"])
logger = logging.getLogger(__name__)


async def _get_or_sync_user(username: str, db: Session) -> User:
    """Return cached user, auto-syncing from GitHub if not found yet."""
    user = db.query(User).filter(User.github_username == username).first()
    if user:
        return user

    # Not in cache — fetch from GitHub transparently
    try:
        user, _ = await sync_profile(db, username, force_refresh=False)
        return user
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


def _analysis_to_response(analysis: CompatibilityAnalysis, username: str) -> CompatibilityResponse:
    return CompatibilityResponse(
        analysis_id=analysis.id,
        username=username,
        match_percentage=analysis.match_percentage,
        recognized_required_languages=analysis.recognized_required_languages or [],
        matched_languages=analysis.matched_languages or [],
        unmatched_languages=analysis.unmatched_languages or [],
        unassessed_keywords=analysis.unassessed_keywords or [],
        score_basis=analysis.score_basis,
        message=(
            "Match based on primary languages in your cached GitHub repositories."
            if analysis.match_percentage is not None
            else "No recognized programming languages were found in the job description."
        ),
    )


@router.post("/analyze", response_model=CompatibilityResponse, status_code=status.HTTP_201_CREATED)
async def analyze(request: CompatibilityRequest, db: Session = Depends(get_db)):
    """
    Vibe Check — auto-syncs profile if needed, then runs compatibility analysis.
    """
    user = await _get_or_sync_user(request.username, db)
    try:
        analysis = analyze_compatibility(db, user, request.job_description)
        return _analysis_to_response(analysis, user.github_username)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "COMPATIBILITY_ERROR", "message": str(exc)},
        )


@router.get("/{analysis_id}", response_model=CompatibilityResponse)
async def get_analysis(analysis_id: int, db: Session = Depends(get_db)):
    """Return a previously stored Vibe Check analysis."""
    analysis = db.query(CompatibilityAnalysis).filter(CompatibilityAnalysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "ANALYSIS_NOT_FOUND", "message": f"Analysis {analysis_id} not found."},
        )
    user = db.query(User).filter(User.id == analysis.user_id).first()
    return _analysis_to_response(analysis, user.github_username if user else "unknown")
