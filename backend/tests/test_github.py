"""Tests for GitHub profile sync API endpoints (mocked GitHub calls)."""

import pytest
from unittest.mock import AsyncMock, patch


class TestProfileSync:
    def test_sync_valid_user(self, client):
        """Successful sync for a valid GitHub username."""
        mock_profile = {
            "login": "octocat", "name": "The Octocat", "bio": "I love code.",
            "avatar_url": "https://avatars.githubusercontent.com/u/583231",
            "html_url": "https://github.com/octocat", "followers": 100,
            "following": 10, "public_repos": 8,
        }
        mock_repos = [
            {
                "id": 1001, "name": "hello-world", "description": "Hello!",
                "language": "Python", "stargazers_count": 25, "forks_count": 8,
                "html_url": "https://github.com/octocat/hello-world",
                "fork": False, "private": False, "updated_at": "2026-10-01T00:00:00Z",
            }
        ]
        with (
            patch("app.services.github_service.fetch_github_profile", new_callable=AsyncMock, return_value=mock_profile),
            patch("app.services.github_service.fetch_github_repositories", new_callable=AsyncMock, return_value=mock_repos),
        ):
            response = client.post("/api/v1/profile/sync", json={"username": "octocat"})
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["username"] == "octocat"
        assert data["cache_status"] in ("miss", "hit", "refresh")

    def test_sync_invalid_user(self, client):
        """Syncing a non-existent GitHub username returns 404."""
        with patch(
            "app.services.github_service.fetch_github_profile",
            new_callable=AsyncMock,
            side_effect=ValueError("GitHub user 'nonexistent_xyz_123' not found."),
        ):
            response = client.post("/api/v1/profile/sync", json={"username": "nonexistent_xyz_123"})
        assert response.status_code == 404
        assert "GITHUB_USER_NOT_FOUND" in str(response.json())

    def test_sync_rate_limit(self, client):
        """Rate limit error returns 503."""
        with patch(
            "app.services.github_service.fetch_github_profile",
            new_callable=AsyncMock,
            side_effect=RuntimeError("GitHub API rate limit exceeded."),
        ):
            response = client.post("/api/v1/profile/sync", json={"username": "someuser"})
        assert response.status_code == 503

    def test_sync_empty_username(self, client):
        """Empty username returns 422 (validation error)."""
        response = client.post("/api/v1/profile/sync", json={"username": "   "})
        # 422 from Pydantic or 404/400 from our sanitizer
        assert response.status_code in (400, 422)

    def test_get_profile_not_synced(self, client):
        """Getting a profile that hasn't been synced returns 404."""
        response = client.get("/api/v1/profile/notyetsynced_xyz")
        assert response.status_code == 404

    def test_cache_hit_on_second_sync(self, client):
        """Second sync within TTL returns cache_status='hit'."""
        mock_profile = {
            "login": "cachetest", "name": "Cache Test", "bio": None,
            "avatar_url": "https://example.com/avatar.png",
            "html_url": "https://github.com/cachetest", "followers": 5,
            "following": 2, "public_repos": 3,
        }
        with (
            patch("app.services.github_service.fetch_github_profile", new_callable=AsyncMock, return_value=mock_profile),
            patch("app.services.github_service.fetch_github_repositories", new_callable=AsyncMock, return_value=[]),
        ):
            # First sync — cache miss
            r1 = client.post("/api/v1/profile/sync", json={"username": "cachetest"})
            assert r1.status_code == 200
            # Second sync without force — cache hit (no GitHub call needed)
            r2 = client.post("/api/v1/profile/sync", json={"username": "cachetest", "force_refresh": False})
            assert r2.status_code == 200
            assert r2.json()["cache_status"] == "hit"
