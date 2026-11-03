"""
SQLAlchemy ORM models for the GitHub Developer Portfolio.

Six core tables:
  users                 – cached GitHub profile per username
  repositories          – cached public repository metadata
  contributions         – daily contribution counts
  user_settings         – theme and basic preferences
  featured_repositories – user-selected showcase repos
  compatibility_analyses – Vibe Check job-description analyses
"""

from datetime import datetime, timezone
from sqlalchemy import (
    Boolean, Column, DateTime, Float, ForeignKey,
    Integer, String, Text, UniqueConstraint, Index, JSON
)
from sqlalchemy.orm import relationship
from app.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    github_username = Column(String(100), nullable=False, unique=True, index=True)
    name = Column(String(255), nullable=True)
    bio = Column(Text, nullable=True)
    avatar_url = Column(Text, nullable=True)
    github_url = Column(Text, nullable=True)
    followers = Column(Integer, nullable=False, default=0)
    following = Column(Integer, nullable=False, default=0)
    public_repos = Column(Integer, nullable=False, default=0)
    total_stars = Column(Integer, nullable=False, default=0)
    total_forks = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=_utcnow)
    updated_at = Column(DateTime, nullable=False, default=_utcnow, onupdate=_utcnow)
    last_synced_at = Column(DateTime, nullable=True)

    # Relationships
    repositories = relationship("Repository", back_populates="user", cascade="all, delete-orphan")
    contributions = relationship("Contribution", back_populates="user", cascade="all, delete-orphan")
    settings = relationship("UserSettings", back_populates="user", uselist=False, cascade="all, delete-orphan")
    featured_repositories = relationship("FeaturedRepository", back_populates="user", cascade="all, delete-orphan")
    compatibility_analyses = relationship("CompatibilityAnalysis", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<User github_username={self.github_username!r}>"


class Repository(Base):
    __tablename__ = "repositories"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    github_repo_id = Column(Integer, nullable=False, unique=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    language = Column(String(100), nullable=True)
    stars = Column(Integer, nullable=False, default=0)
    forks = Column(Integer, nullable=False, default=0)
    html_url = Column(Text, nullable=False)
    is_fork = Column(Boolean, nullable=False, default=False)
    is_private = Column(Boolean, nullable=False, default=False)
    updated_at = Column(DateTime, nullable=True)   # GitHub repo updated_at
    cached_at = Column(DateTime, nullable=False, default=_utcnow)

    __table_args__ = (
        Index("ix_repositories_user_id_stars", "user_id", "stars"),
    )

    # Relationships
    user = relationship("User", back_populates="repositories")
    featured_by = relationship("FeaturedRepository", back_populates="repository", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Repository name={self.name!r} user_id={self.user_id}>"


class Contribution(Base):
    __tablename__ = "contributions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    contribution_date = Column(String(10), nullable=False)  # ISO date "YYYY-MM-DD"
    contribution_count = Column(Integer, nullable=False, default=0)
    cached_at = Column(DateTime, nullable=False, default=_utcnow)

    __table_args__ = (
        UniqueConstraint("user_id", "contribution_date", name="uq_contributions_user_date"),
    )

    user = relationship("User", back_populates="contributions")

    def __repr__(self) -> str:
        return f"<Contribution date={self.contribution_date} count={self.contribution_count}>"


class UserSettings(Base):
    __tablename__ = "user_settings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    theme = Column(String(20), nullable=False, default="light")
    created_at = Column(DateTime, nullable=False, default=_utcnow)
    updated_at = Column(DateTime, nullable=False, default=_utcnow, onupdate=_utcnow)

    user = relationship("User", back_populates="settings")


class FeaturedRepository(Base):
    __tablename__ = "featured_repositories"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    repository_id = Column(Integer, ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False)
    display_order = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=_utcnow)

    __table_args__ = (
        UniqueConstraint("user_id", "repository_id", name="uq_featured_user_repo"),
    )

    user = relationship("User", back_populates="featured_repositories")
    repository = relationship("Repository", back_populates="featured_by")


class CompatibilityAnalysis(Base):
    __tablename__ = "compatibility_analyses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    job_description = Column(Text, nullable=False)
    match_percentage = Column(Float, nullable=True)  # null when no recognized languages
    recognized_required_languages = Column(JSON, nullable=False, default=list)
    matched_languages = Column(JSON, nullable=False, default=list)
    unmatched_languages = Column(JSON, nullable=False, default=list)
    unassessed_keywords = Column(JSON, nullable=False, default=list)
    score_basis = Column(String(100), nullable=False, default="distinct_primary_languages_in_cached_repositories")
    analyzed_at = Column(DateTime, nullable=False, default=_utcnow)

    user = relationship("User", back_populates="compatibility_analyses")

    def __repr__(self) -> str:
        return f"<CompatibilityAnalysis id={self.id} match={self.match_percentage}>"
