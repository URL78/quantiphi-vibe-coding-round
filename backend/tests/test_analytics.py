"""Tests for analytics service — language distribution and streak calculation."""

import pytest
from datetime import date, timedelta
from unittest.mock import MagicMock

from app.services.analytics_service import calculate_streaks, get_language_distribution


class TestLanguageDistribution:
    def test_basic_distribution(self, db):
        """Language distribution is computed correctly from repos."""
        from app.models.models import Repository, User
        from app.utils.helpers import utcnow

        user = User(
            github_username="testlang",
            followers=0, following=0, public_repos=3,
            total_stars=0, total_forks=0,
            created_at=utcnow(), updated_at=utcnow(),
        )
        db.add(user)
        db.flush()

        for lang, name in [("Python", "repo1"), ("Python", "repo2"), ("JavaScript", "repo3")]:
            db.add(Repository(
                user_id=user.id, github_repo_id=hash(name), name=name,
                language=lang, stars=0, forks=0,
                html_url=f"https://github.com/test/{name}",
                cached_at=utcnow(),
            ))
        db.flush()

        dist = get_language_distribution(db, user)
        langs = {d["name"]: d for d in dist}

        assert "Python" in langs
        assert "JavaScript" in langs
        assert langs["Python"]["repository_count"] == 2
        assert langs["JavaScript"]["repository_count"] == 1
        assert abs(langs["Python"]["percentage"] - 66.7) < 1
        assert abs(langs["JavaScript"]["percentage"] - 33.3) < 1

    def test_repos_without_language_excluded(self, db):
        """Repos with no language metadata must not skew percentages."""
        from app.models.models import Repository, User
        from app.utils.helpers import utcnow

        user = User(
            github_username="testnolang",
            followers=0, following=0, public_repos=2,
            total_stars=0, total_forks=0,
            created_at=utcnow(), updated_at=utcnow(),
        )
        db.add(user)
        db.flush()

        db.add(Repository(
            user_id=user.id, github_repo_id=99991, name="with_lang",
            language="Rust", stars=0, forks=0,
            html_url="https://github.com/x/y", cached_at=utcnow(),
        ))
        db.add(Repository(
            user_id=user.id, github_repo_id=99992, name="no_lang",
            language=None, stars=0, forks=0,
            html_url="https://github.com/x/z", cached_at=utcnow(),
        ))
        db.flush()

        dist = get_language_distribution(db, user)
        assert len(dist) == 1
        assert dist[0]["name"] == "Rust"
        assert dist[0]["percentage"] == 100.0


class TestStreaks:
    def _make_user(self, db):
        from app.models.models import User
        from app.utils.helpers import utcnow
        user = User(
            github_username=f"streaktest_{id(self)}",
            followers=0, following=0, public_repos=0,
            total_stars=0, total_forks=0,
            created_at=utcnow(), updated_at=utcnow(),
        )
        db.add(user)
        db.flush()
        return user

    def _add_contributions(self, db, user, dates_with_counts):
        from app.models.models import Contribution
        from app.utils.helpers import utcnow
        for d, count in dates_with_counts:
            db.add(Contribution(
                user_id=user.id,
                contribution_date=d.isoformat() if isinstance(d, date) else d,
                contribution_count=count,
                cached_at=utcnow(),
            ))
        db.flush()

    def test_no_contributions_returns_zeros(self, db):
        user = self._make_user(db)
        result = calculate_streaks(db, user)
        assert result["current_streak"] == 0
        assert result["longest_streak"] == 0
        assert result["last_contribution_date"] is None

    def test_longest_streak_calculation(self, db):
        user = self._make_user(db)
        today = date.today()
        dates = [(today - timedelta(days=i), 2) for i in range(5)]  # 5 consecutive days
        self._add_contributions(db, user, dates)

        result = calculate_streaks(db, user)
        assert result["longest_streak"] == 5

    def test_streak_broken_by_zero_day(self, db):
        user = self._make_user(db)
        today = date.today()
        # 3 days, gap, then 2 days
        dates = [
            (today - timedelta(days=6), 1),
            (today - timedelta(days=5), 1),
            (today - timedelta(days=4), 1),
            # day -3: gap
            (today - timedelta(days=2), 1),
            (today - timedelta(days=1), 1),
        ]
        self._add_contributions(db, user, dates)
        result = calculate_streaks(db, user)
        assert result["longest_streak"] == 3

    def test_last_contribution_date(self, db):
        user = self._make_user(db)
        d = date(2026, 10, 15)
        self._add_contributions(db, user, [(d, 5)])
        result = calculate_streaks(db, user)
        assert result["last_contribution_date"] == "2026-10-15"
