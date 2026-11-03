"""
GitHub API integration service.

Handles both REST API (profile, repositories) and GraphQL API (contributions).
All external GitHub requests go through this service — never from the browser.

Rate limit handling:
  - REST: checks X-RateLimit-Remaining header
  - GraphQL: requires a valid GitHub token; gracefully fails when absent
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

GITHUB_API_BASE = settings.github_api_base
GITHUB_GRAPHQL_URL = settings.github_graphql_url

CONTRIBUTION_GRAPHQL_QUERY = """
query($username: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $username) {
    contributionsCollection(from: $from, to: $to) {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays {
            date
            contributionCount
          }
        }
      }
    }
  }
}
"""


def _build_headers() -> Dict[str, str]:
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "GitHub-Developer-Portfolio/1.0",
    }
    if settings.github_token:
        headers["Authorization"] = f"Bearer {settings.github_token}"
    return headers


def _check_rate_limit(response: httpx.Response) -> None:
    remaining = response.headers.get("X-RateLimit-Remaining")
    if remaining is not None and int(remaining) == 0:
        reset_ts = response.headers.get("X-RateLimit-Reset")
        raise RuntimeError(
            f"GitHub API rate limit exceeded. Resets at {reset_ts}."
        )


async def fetch_github_profile(username: str) -> Dict[str, Any]:
    """Fetch a public GitHub user profile via REST API."""
    async with httpx.AsyncClient(timeout=settings.request_timeout) as client:
        response = await client.get(
            f"{GITHUB_API_BASE}/users/{username}",
            headers=_build_headers(),
        )
        if response.status_code == 404:
            raise ValueError(f"GitHub user '{username}' not found.")
        if response.status_code == 403:
            _check_rate_limit(response)
            raise RuntimeError("GitHub API access forbidden.")
        if response.status_code == 401:
            raise RuntimeError("GitHub API authentication failed. Check GITHUB_TOKEN.")
        response.raise_for_status()
        return response.json()


async def fetch_github_repositories(username: str) -> List[Dict[str, Any]]:
    """Fetch all PUBLIC repositories for a GitHub user (handles pagination)."""
    repos: List[Dict[str, Any]] = []
    page = 1
    per_page = 100

    async with httpx.AsyncClient(timeout=settings.request_timeout) as client:
        while True:
            response = await client.get(
                f"{GITHUB_API_BASE}/users/{username}/repos",
                headers=_build_headers(),
                params={"type": "public", "per_page": per_page, "page": page, "sort": "updated"},
            )
            if response.status_code == 403:
                _check_rate_limit(response)
                raise RuntimeError("GitHub API rate limit exceeded.")
            if response.status_code == 404:
                raise ValueError(f"GitHub user '{username}' not found.")
            response.raise_for_status()
            batch = response.json()
            if not batch:
                break
            repos.extend(batch)
            if len(batch) < per_page:
                break
            page += 1

    return repos


async def fetch_contributions(username: str, weeks: int = 52) -> Optional[Dict[str, Any]]:
    """
    Fetch daily contribution calendar via GitHub GraphQL API.
    Requires a GitHub token. Returns None gracefully if unavailable.
    """
    if not settings.github_token:
        logger.warning("GITHUB_TOKEN not set — contribution heatmap unavailable.")
        return None

    to_dt = datetime.now(timezone.utc)
    from_dt = to_dt - timedelta(weeks=weeks)

    variables = {
        "username": username,
        "from": from_dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "to": to_dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
    }

    async with httpx.AsyncClient(timeout=settings.request_timeout) as client:
        response = await client.post(
            GITHUB_GRAPHQL_URL,
            headers=_build_headers(),
            json={"query": CONTRIBUTION_GRAPHQL_QUERY, "variables": variables},
        )
        if response.status_code == 401:
            logger.warning("GraphQL auth failed — contribution data unavailable.")
            return None
        if response.status_code == 403:
            logger.warning("GraphQL rate limit hit — contribution data unavailable.")
            return None
        if not response.is_success:
            logger.warning("GraphQL request failed with status %d", response.status_code)
            return None

        data = response.json()
        if "errors" in data:
            logger.warning("GraphQL errors: %s", data["errors"])
            return None

        user_data = data.get("data", {}).get("user")
        if not user_data:
            logger.warning("GraphQL returned no user data for '%s'.", username)
            return None

        return user_data.get("contributionsCollection", {}).get("contributionCalendar")


def normalize_profile(raw: Dict[str, Any]) -> Dict[str, Any]:
    """Map GitHub REST profile response to application fields."""
    return {
        "github_username": raw.get("login", ""),
        "name": raw.get("name"),
        "bio": raw.get("bio"),
        "avatar_url": raw.get("avatar_url"),
        "github_url": raw.get("html_url"),
        "followers": raw.get("followers", 0) or 0,
        "following": raw.get("following", 0) or 0,
        "public_repos": raw.get("public_repos", 0) or 0,
    }


def normalize_repository(raw: Dict[str, Any]) -> Dict[str, Any]:
    """Map GitHub REST repository response to application fields."""
    updated_at_str = raw.get("updated_at")
    updated_at = None
    if updated_at_str:
        try:
            updated_at = datetime.fromisoformat(updated_at_str.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            pass

    return {
        "github_repo_id": raw["id"],
        "name": raw.get("name", ""),
        "description": raw.get("description"),
        "language": raw.get("language"),
        "stars": raw.get("stargazers_count", 0) or 0,
        "forks": raw.get("forks_count", 0) or 0,
        "html_url": raw.get("html_url", ""),
        "is_fork": raw.get("fork", False),
        "is_private": raw.get("private", False),
        "updated_at": updated_at,
    }
