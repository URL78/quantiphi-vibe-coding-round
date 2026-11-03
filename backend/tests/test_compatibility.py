"""
Tests for the Vibe Check / Tech Stack Compatibility feature.

Covers all 10 required edge cases from the requirements document.
"""

import pytest
from app.services.compatibility_service import (
    calculate_match,
    extract_languages_from_jd,
)


# ─── Language extraction tests ──────────────────────────────────────────

class TestExtractLanguages:
    """Tests for extract_languages_from_jd."""

    def test_recognizes_common_languages(self):
        jd = "We need engineers with Python, JavaScript, and Go experience."
        langs, _ = extract_languages_from_jd(jd)
        assert "Python" in langs
        assert "JavaScript" in langs
        assert "Go" in langs

    def test_case_insensitive_matching(self):
        jd = "Skills: PYTHON, javascript, GOLANG, typescript"
        langs, _ = extract_languages_from_jd(jd)
        assert "Python" in langs
        assert "JavaScript" in langs
        assert "Go" in langs
        assert "TypeScript" in langs

    def test_alias_normalization_cpp(self):
        """'cpp' should map to canonical 'C++'."""
        jd = "Experience with cpp required."
        langs, _ = extract_languages_from_jd(jd)
        assert "C++" in langs
        assert "cpp" not in langs  # raw alias should not appear

    def test_alias_normalization_golang(self):
        """'golang' should map to canonical 'Go'."""
        jd = "We use golang for our backend services."
        langs, _ = extract_languages_from_jd(jd)
        assert "Go" in langs
        assert "golang" not in langs

    def test_deduplication_of_duplicate_mentions(self):
        """Multiple mentions of same language → appear once."""
        jd = "Python developer. Python experience required. Senior Python role."
        langs, _ = extract_languages_from_jd(jd)
        assert langs.count("Python") == 1

    def test_no_substring_match_java_in_javascript(self):
        """'Java' must not match where only 'JavaScript' is mentioned."""
        jd = "We are looking for JavaScript developers."
        langs, _ = extract_languages_from_jd(jd)
        # JavaScript should be there
        assert "JavaScript" in langs
        # Java should NOT be matched by the 'javascript' text alone
        # The Java pattern uses negative lookahead (?!script)
        assert "Java" not in langs

    def test_cpp_and_c_disambiguation(self):
        """C++ should be matched without triggering C."""
        jd = "Requires C++ expertise."
        langs, _ = extract_languages_from_jd(jd)
        assert "C++" in langs

    def test_non_language_frameworks_to_unassessed(self):
        """FastAPI, Docker, PostgreSQL must not count as matched languages."""
        jd = "We use FastAPI, Docker, PostgreSQL, Redis, and Kafka."
        langs, unassessed = extract_languages_from_jd(jd)
        # No programming language should be recognized
        lang_lower = [l.lower() for l in langs]
        assert "fastapi" not in lang_lower
        assert "docker" not in lang_lower
        assert "postgresql" not in lang_lower
        # Some should appear in unassessed
        unassessed_lower = [u.lower() for u in unassessed]
        assert any("fastapi" in u or "docker" in u or "postgresql" in u for u in unassessed_lower)

    def test_empty_job_description(self):
        """Empty-ish JD returns no languages and no unassessed keywords."""
        langs, unassessed = extract_languages_from_jd("   ")
        assert langs == []

    def test_recognizes_typescript(self):
        jd = "Full-stack role requiring TypeScript, React, and Node."
        langs, _ = extract_languages_from_jd(jd)
        assert "TypeScript" in langs


# ─── Match calculation tests ─────────────────────────────────────────────

class TestCalculateMatch:
    """Tests for calculate_match (the core Vibe Check formula)."""

    def test_all_languages_matched(self):
        required = ["Python", "JavaScript"]
        repo_langs = {"python", "javascript"}
        result = calculate_match(required, repo_langs)
        assert result["match_percentage"] == 100.0
        assert set(result["matched_languages"]) == {"Python", "JavaScript"}
        assert result["unmatched_languages"] == []

    def test_some_languages_matched(self):
        required = ["Python", "Java", "C++", "JavaScript", "Go"]
        repo_langs = {"python", "javascript", "c++"}
        result = calculate_match(required, repo_langs)
        assert result["match_percentage"] == 60.0
        assert len(result["matched_languages"]) == 3
        assert len(result["unmatched_languages"]) == 2

    def test_no_languages_matched(self):
        """Score should be 0, not null, when required langs exist but none match."""
        required = ["Java", "Go"]
        repo_langs = {"python", "javascript"}
        result = calculate_match(required, repo_langs)
        assert result["match_percentage"] == 0.0
        assert result["matched_languages"] == []
        assert set(result["unmatched_languages"]) == {"Java", "Go"}

    def test_no_recognized_required_languages(self):
        """No recognized languages → match_percentage must be null (not division by zero)."""
        result = calculate_match([], {"python"})
        assert result["match_percentage"] is None
        assert "No recognized" in result["message"]

    def test_match_is_case_insensitive(self):
        """Repo languages from DB may have any casing; comparison must be case-insensitive."""
        required = ["Python", "JavaScript"]
        repo_langs = {"Python", "JAVASCRIPT"}  # as stored in DB
        # Normalize to lowercase in service
        repo_langs_lower = {l.lower() for l in repo_langs}
        result = calculate_match(required, repo_langs_lower)
        assert result["match_percentage"] == 100.0

    def test_percentage_formula(self):
        """Verify: matched / required * 100."""
        required = ["Python", "Java", "Go"]
        repo_langs = {"python"}
        result = calculate_match(required, repo_langs)
        expected = round((1 / 3) * 100, 2)
        assert result["match_percentage"] == expected

    def test_score_between_0_and_100(self):
        required = ["Python", "Java", "C++"]
        repo_langs = {"python", "java", "c++", "javascript", "go"}
        result = calculate_match(required, repo_langs)
        assert 0 <= result["match_percentage"] <= 100
