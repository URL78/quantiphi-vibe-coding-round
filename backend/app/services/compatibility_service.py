"""
Vibe Check / Tech Stack Compatibility Service (MANDATORY FEATURE).

Algorithm:
  1. Extract recognized programming languages from the job description
     using a predefined alias dictionary and word-boundary regex.
  2. Normalize all aliases to canonical language names.
  3. Read the distinct primary languages from the user's cached repositories in SQLite.
  4. Compare the two sets.
  5. Calculate: match_percentage = matched / required * 100
  6. Persist the analysis in compatibility_analyses table.

Edge cases handled:
  - No recognized languages  → match_percentage = null, clear message
  - No cached repositories   → clear error prompting sync
  - No matching languages    → score of 0 (not null)
  - Duplicate / alias names  → deduplicated to canonical before comparison
  - Substring traps          → word-boundary regex prevents false matches
  - Case insensitivity       → all matching is lowercased
"""

import logging
import re
from typing import Any, Dict, List, Optional, Set, Tuple

from sqlalchemy.orm import Session

from app.models.models import CompatibilityAnalysis, Repository, User
from app.utils.helpers import utcnow
from app.utils.language_dict import (
    LANGUAGE_DEFINITIONS,
    NON_LANGUAGE_KEYWORDS,
)

logger = logging.getLogger(__name__)


# ─── Language extraction ─────────────────────────────────────────────────


def _build_patterns() -> List[Tuple[str, List[re.Pattern]]]:
    """
    Compile regex patterns for each language once at module load time.
    Returns list of (canonical_name, [compiled patterns]) ordered as defined.
    """
    compiled: List[Tuple[str, List[re.Pattern]]] = []
    for canonical, aliases in LANGUAGE_DEFINITIONS:
        patterns = []
        for alias in aliases:
            # Aliases may already contain regex like \b or (?!...)
            # Wrap in word-boundary only if alias does NOT already start with \b or (?
            if alias.startswith("\\b") or alias.startswith("(?"):
                pattern_str = alias
            else:
                pattern_str = r"\b" + re.escape(alias) + r"\b"
            try:
                patterns.append(re.compile(pattern_str, re.IGNORECASE))
            except re.error as e:
                logger.warning("Invalid regex for '%s' alias '%s': %s", canonical, alias, e)
        compiled.append((canonical, patterns))
    return compiled


_COMPILED_PATTERNS = _build_patterns()

# Non-language keyword patterns (for unassessed_keywords)
_NON_LANG_PATTERNS = [
    (kw, re.compile(r"\b" + re.escape(kw) + r"\b", re.IGNORECASE))
    for kw in NON_LANGUAGE_KEYWORDS
]


def extract_languages_from_jd(
    job_description: str,
) -> Tuple[List[str], List[str]]:
    """
    Extract recognized programming languages and unassessed tech keywords.

    Returns:
        (recognized_programming_languages, unassessed_keywords)
    Both lists contain deduplicated, canonical-name values.
    """
    recognized: Set[str] = set()
    unassessed: Set[str] = set()

    # Match languages (ordered: most specific alias first)
    for canonical, patterns in _COMPILED_PATTERNS:
        for pattern in patterns:
            if pattern.search(job_description):
                recognized.add(canonical)
                break  # canonical already matched, move to next language

    # Match non-language keywords
    for keyword, pattern in _NON_LANG_PATTERNS:
        if pattern.search(job_description):
            unassessed.add(keyword)

    # Remove any canonical language name that may also appear in unassessed
    # (frameworks named after languages, e.g. "Go" vs "golang")
    unassessed -= recognized

    return sorted(recognized), sorted(unassessed)


# ─── Repository language retrieval ───────────────────────────────────────


def get_repo_languages(db: Session, user: User) -> Set[str]:
    """
    Return the set of distinct, lowercased primary languages
    from the user's cached repositories (excluding None/empty).
    """
    repos = (
        db.query(Repository.language)
        .filter(Repository.user_id == user.id, Repository.language.isnot(None))
        .all()
    )
    return {row.language.strip().lower() for row in repos if row.language and row.language.strip()}


# ─── Match calculation ───────────────────────────────────────────────────


def calculate_match(
    recognized_languages: List[str],
    repo_languages: Set[str],
) -> Dict[str, Any]:
    """
    Compare required languages against cached repo languages.
    Returns match stats dict.
    """
    if not recognized_languages:
        return {
            "match_percentage": None,
            "matched_languages": [],
            "unmatched_languages": [],
            "message": "No recognized programming-language requirements were found in the job description.",
        }

    matched: List[str] = []
    unmatched: List[str] = []

    for lang in recognized_languages:
        if lang.lower() in repo_languages:
            matched.append(lang)
        else:
            unmatched.append(lang)

    match_pct = round((len(matched) / len(recognized_languages)) * 100, 2)

    return {
        "match_percentage": match_pct,
        "matched_languages": matched,
        "unmatched_languages": unmatched,
        "message": "GitHub evidence-based compatibility estimate.",
    }


# ─── Full Vibe Check analysis ─────────────────────────────────────────────


def analyze_compatibility(
    db: Session,
    user: User,
    job_description: str,
) -> CompatibilityAnalysis:
    """
    Full Vibe Check pipeline:
      extract → compare → calculate → persist → return.
    """
    # Check for cached repos
    repo_count = db.query(Repository).filter(Repository.user_id == user.id).count()
    if repo_count == 0:
        raise ValueError(
            "No cached repositories found. Please sync your GitHub profile first."
        )

    # Extract languages from job description
    recognized_langs, unassessed_kws = extract_languages_from_jd(job_description)

    # Get user's repo languages from SQLite (no GitHub call needed)
    repo_languages = get_repo_languages(db, user)

    # Calculate match
    match_result = calculate_match(recognized_langs, repo_languages)

    # Persist analysis
    analysis = CompatibilityAnalysis(
        user_id=user.id,
        job_description=job_description,
        match_percentage=match_result["match_percentage"],
        recognized_required_languages=recognized_langs,
        matched_languages=match_result["matched_languages"],
        unmatched_languages=match_result["unmatched_languages"],
        unassessed_keywords=unassessed_kws,
        score_basis="distinct_primary_languages_in_cached_repositories",
        analyzed_at=utcnow(),
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    return analysis
