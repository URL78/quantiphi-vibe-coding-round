"""Repository endpoints — list, get, featured toggle."""

import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import desc, asc
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import FeaturedRepository, Repository, User
from app.schemas.schemas import (
    FeaturedPatchRequest, FeaturedPatchResponse,
    RepositoryListResponse, RepositoryOut,
)
from app.utils.helpers import utcnow

router = APIRouter(prefix="/repositories", tags=["Repositories"])
logger = logging.getLogger(__name__)


def _get_user_or_404(username: str, db: Session) -> User:
    user = db.query(User).filter(User.github_username == username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "USER_NOT_FOUND", "message": f"No cached profile for '{username}'."},
        )
    return user


@router.get("/{username}", response_model=RepositoryListResponse)
async def list_repositories(
    username: str,
    sort_by: str = Query(default="stars", pattern="^(stars|updated_at|name)$"),
    order: str = Query(default="desc", pattern="^(asc|desc)$"),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=12, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Return paginated, sorted repositories for a user."""
    user = _get_user_or_404(username, db)

    # Determine featured repo IDs
    featured_ids = {
        fr.repository_id
        for fr in db.query(FeaturedRepository).filter(FeaturedRepository.user_id == user.id).all()
    }

    # Build query
    query = db.query(Repository).filter(Repository.user_id == user.id)
    sort_column = {"stars": Repository.stars, "updated_at": Repository.updated_at, "name": Repository.name}[sort_by]
    query = query.order_by(desc(sort_column) if order == "desc" else asc(sort_column))

    total = query.count()
    repos = query.offset((page - 1) * limit).limit(limit).all()

    return RepositoryListResponse(
        username=user.github_username,
        total=total,
        page=page,
        limit=limit,
        repositories=[
            RepositoryOut(
                **{c.name: getattr(repo, c.name) for c in repo.__table__.columns},
                featured=repo.id in featured_ids,
            )
            for repo in repos
        ],
    )


@router.get("/{username}/{repo_name}", response_model=RepositoryOut)
async def get_repository(username: str, repo_name: str, db: Session = Depends(get_db)):
    """Return a single cached repository."""
    user = _get_user_or_404(username, db)
    repo = (
        db.query(Repository)
        .filter(Repository.user_id == user.id, Repository.name == repo_name)
        .first()
    )
    if not repo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "REPO_NOT_FOUND", "message": f"Repository '{repo_name}' not found."},
        )
    featured_ids = {
        fr.repository_id
        for fr in db.query(FeaturedRepository).filter(FeaturedRepository.user_id == user.id).all()
    }
    return RepositoryOut(
        **{c.name: getattr(repo, c.name) for c in repo.__table__.columns},
        featured=repo.id in featured_ids,
    )


@router.patch("/{username}/{repo_name}/featured", response_model=FeaturedPatchResponse)
async def toggle_featured(
    username: str,
    repo_name: str,
    payload: FeaturedPatchRequest,
    db: Session = Depends(get_db),
):
    """Toggle the featured status of a repository for a user."""
    user = _get_user_or_404(username, db)
    repo = (
        db.query(Repository)
        .filter(Repository.user_id == user.id, Repository.name == repo_name)
        .first()
    )
    if not repo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "REPO_NOT_FOUND", "message": f"Repository '{repo_name}' not found."},
        )

    existing = (
        db.query(FeaturedRepository)
        .filter(
            FeaturedRepository.user_id == user.id,
            FeaturedRepository.repository_id == repo.id,
        )
        .first()
    )

    if payload.featured:
        if existing is None:
            fr = FeaturedRepository(
                user_id=user.id,
                repository_id=repo.id,
                display_order=payload.display_order,
                created_at=utcnow(),
            )
            db.add(fr)
        else:
            existing.display_order = payload.display_order
    else:
        if existing:
            db.delete(existing)

    db.commit()
    return FeaturedPatchResponse(
        success=True,
        repository=repo.name,
        featured=payload.featured,
        display_order=payload.display_order,
    )
