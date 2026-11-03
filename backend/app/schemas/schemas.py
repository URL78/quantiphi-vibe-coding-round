"""
Pydantic schemas for request/response validation.

Follows the API contracts defined in docs/API_DOCUMENTATION.md.
All schemas use snake_case.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator


# ─── Shared error shape ────────────────────────────────────────────────
class ErrorDetail(BaseModel):
    code: str
    message: str


# ─── Profile ───────────────────────────────────────────────────────────
class ProfileSyncRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=100)
    force_refresh: bool = False

    @field_validator("username")
    @classmethod
    def strip_username(cls, v: str) -> str:
        return v.strip()


class ProfileSyncResponse(BaseModel):
    success: bool
    username: str
    message: str
    cache_status: str  # "hit" | "miss" | "stale"
    last_synced_at: Optional[datetime]


class ProfileResponse(BaseModel):
    id: int
    github_username: str
    name: Optional[str]
    bio: Optional[str]
    avatar_url: Optional[str]
    github_url: Optional[str]
    followers: int
    following: int
    public_repos: int
    total_stars: int
    total_forks: int
    last_synced_at: Optional[datetime]
    is_stale: bool = False

    model_config = {"from_attributes": True}


# ─── Analytics ─────────────────────────────────────────────────────────
class AnalyticsResponse(BaseModel):
    username: str
    followers: int
    following: int
    public_repos: int
    total_stars: int
    total_forks: int
    total_contributions: int
    is_stale: bool = False


class LanguageStat(BaseModel):
    name: str
    repository_count: int
    percentage: float


class LanguagesResponse(BaseModel):
    username: str
    basis: str = "repository_count"
    languages: List[LanguageStat]


# ─── Contributions ─────────────────────────────────────────────────────
class ContributionDay(BaseModel):
    date: str
    count: int
    intensity: int  # 0–4


class ContributionsResponse(BaseModel):
    username: str
    total_contributions: int
    contributions: List[ContributionDay]
    is_stale: bool = False


class StreakResponse(BaseModel):
    username: str
    current_streak: int
    longest_streak: int
    last_contribution_date: Optional[str]


# ─── Repositories ──────────────────────────────────────────────────────
class RepositoryOut(BaseModel):
    id: int
    github_repo_id: int
    name: str
    description: Optional[str]
    language: Optional[str]
    stars: int
    forks: int
    html_url: str
    is_fork: bool
    updated_at: Optional[datetime]
    featured: bool = False

    model_config = {"from_attributes": True}


class RepositoryListResponse(BaseModel):
    username: str
    total: int
    page: int
    limit: int
    repositories: List[RepositoryOut]


class FeaturedPatchRequest(BaseModel):
    featured: bool
    display_order: int = 0


class FeaturedPatchResponse(BaseModel):
    success: bool
    repository: str
    featured: bool
    display_order: int


# ─── Compatibility / Vibe Check ────────────────────────────────────────
class CompatibilityRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=100)
    job_description: str = Field(..., min_length=1, max_length=10000)

    @field_validator("username")
    @classmethod
    def strip_username(cls, v: str) -> str:
        return v.strip()

    @field_validator("job_description")
    @classmethod
    def strip_jd(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("Job description cannot be empty.")
        return stripped


class CompatibilityResponse(BaseModel):
    analysis_id: int
    username: str
    match_percentage: Optional[float]
    recognized_required_languages: List[str]
    matched_languages: List[str]
    unmatched_languages: List[str]
    unassessed_keywords: List[str]
    score_basis: str
    message: str


# ─── Career Recommendations ────────────────────────────────────────────
class Recommendation(BaseModel):
    skill: str
    suggestion: str


class CareerRecommendationsResponse(BaseModel):
    analysis_id: int
    recommendations: List[Recommendation]


# ─── DeepWiki ──────────────────────────────────────────────────────────
class DeepWikiAskRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)


class DeepWikiAskResponse(BaseModel):
    owner: str
    repository: str
    question: str
    answer: str
    source: str = "DeepWiki"


class DeepWikiStructureResponse(BaseModel):
    owner: str
    repository: str
    structure: Any


class DeepWikiContentsResponse(BaseModel):
    owner: str
    repository: str
    contents: Any


# ─── Interview ─────────────────────────────────────────────────────────
class InterviewGenerateRequest(BaseModel):
    username: str
    repository: str
    difficulty: str = Field(default="medium", pattern="^(easy|medium|hard)$")
    number_of_questions: int = Field(default=5, ge=1, le=10)


class InterviewGenerateResponse(BaseModel):
    repository: str
    questions: List[str]


class InterviewEvaluateRequest(BaseModel):
    owner: str
    repository: str
    question: str
    answer: str = Field(..., min_length=1, max_length=5000)


class InterviewEvaluateResponse(BaseModel):
    feedback: str
    strengths: List[str]
    improvements: List[str]
    context_available: bool


# ─── Settings ──────────────────────────────────────────────────────────
class SettingsResponse(BaseModel):
    username: str
    theme: str


class SettingsUpdateRequest(BaseModel):
    theme: str = Field(..., pattern="^(light|dark)$")


# ─── Portfolio ─────────────────────────────────────────────────────────
class PortfolioResponse(BaseModel):
    profile: ProfileResponse
    analytics: AnalyticsResponse
    languages: List[LanguageStat]
    featured_repositories: List[RepositoryOut]
    latest_analysis: Optional[CompatibilityResponse]
