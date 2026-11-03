"""
Portfolio service — composes the public portfolio view for a GitHub username.

Returns profile, analytics, language distribution, featured repositories,
and latest Vibe Check analysis (if any exists).
"""

from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from app.models.models import CompatibilityAnalysis, FeaturedRepository, Repository, User
from app.services.analytics_service import get_language_distribution, get_total_contributions


def get_portfolio(db: Session, user: User) -> Dict[str, Any]:
    """Compose a public portfolio response."""

    # Language distribution
    languages = get_language_distribution(db, user)

    # Featured repositories (ordered)
    featured_links = (
        db.query(FeaturedRepository)
        .filter(FeaturedRepository.user_id == user.id)
        .order_by(FeaturedRepository.display_order.asc())
        .all()
    )

    featured_repos = []
    featured_ids = {fl.repository_id for fl in featured_links}
    for fl in featured_links:
        repo = db.query(Repository).filter(Repository.id == fl.repository_id).first()
        if repo:
            featured_repos.append(repo)

    # Latest compatibility analysis (most recent)
    latest_analysis: Optional[CompatibilityAnalysis] = (
        db.query(CompatibilityAnalysis)
        .filter(CompatibilityAnalysis.user_id == user.id)
        .order_by(CompatibilityAnalysis.analyzed_at.desc())
        .first()
    )

    # Total contributions
    total_contributions = get_total_contributions(db, user)

    return {
        "profile": user,
        "analytics": {
            "username": user.github_username,
            "followers": user.followers,
            "following": user.following,
            "public_repos": user.public_repos,
            "total_stars": user.total_stars,
            "total_forks": user.total_forks,
            "total_contributions": total_contributions,
            "is_stale": False,
        },
        "languages": languages,
        "featured_repositories": featured_repos,
        "featured_ids": featured_ids,
        "latest_analysis": latest_analysis,
    }
