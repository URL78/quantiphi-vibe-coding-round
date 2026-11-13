"""
Vibe Check – Tech Stack Compatibility Service (MANDATORY FEATURE).

Algorithm
─────────
1. Lowercase the entire job description.
2. For each known language, check if any of its aliases appear in the text.
3. Build the set of "recognized required languages" from the JD.
4. Load the user's distinct cached repository primary languages from SQLite.
5. Intersect the two sets → matched / unmatched.
6. match_percentage = len(matched) / len(required) × 100
   (null when required set is empty — avoids division by zero)
7. Persist result in compatibility_analyses table.

Key design decisions
────────────────────
- Each alias in LANGUAGE_DEFINITIONS is a plain lowercase string.
  Pattern building happens here, with special handling for:
    - Languages ending in non-word chars (C++, C#, F#) → custom boundary
    - JavaScript-before-Java disambiguation (strip JS before checking Java)
    - 'go' alone is too ambiguous → only match 'golang'/'go language'
- Frameworks / tools go to unassessed_keywords, not the language score.
"""

import logging
import re
from typing import Any, Dict, List, Set, Tuple

from sqlalchemy.orm import Session

from app.models.models import CompatibilityAnalysis, Repository, User
from app.utils.helpers import utcnow
from app.utils.language_dict import LANGUAGE_DEFINITIONS, NON_LANGUAGE_KEYWORDS

logger = logging.getLogger(__name__)


# ─── Pattern compilation ──────────────────────────────────────────────────────

def _make_pattern(alias: str) -> re.Pattern:
    """
    Build a safe, word-boundary-aware pattern for a plain alias string.

    For aliases ending in a non-word character (like '+' in 'c++' or '#' in 'c#'),
    standard \b doesn't work. We use a negative lookahead/lookbehind instead.
    """
    # Escape the alias so it matches literally
    escaped = re.escape(alias)

    # Determine if the alias starts/ends with word chars
    starts_word = bool(re.match(r'\w', alias[0]))
    ends_word   = bool(re.match(r'\w', alias[-1]))

    prefix = r'\b'   if starts_word else r'(?<!\w)'
    suffix = r'\b'   if ends_word   else r'(?!\w)'

    return re.compile(prefix + escaped + suffix, re.IGNORECASE)


# Build once at module load — (canonical_name, [compiled_patterns])
_LANG_PATTERNS: List[Tuple[str, List[re.Pattern]]] = [
    (canonical, [_make_pattern(a) for a in aliases])
    for canonical, aliases in LANGUAGE_DEFINITIONS
]

_NON_LANG_PATTERNS: List[Tuple[str, re.Pattern]] = [
    (kw, _make_pattern(kw)) for kw in NON_LANGUAGE_KEYWORDS
]


# ─── Language extraction ──────────────────────────────────────────────────────

def extract_languages_from_jd(jd: str) -> Tuple[List[str], List[str]]:
    """
    Return (recognized_languages, unassessed_tech_keywords).
    """
    # Strip 'javascript' occurrences before checking for plain 'java'
    jd_no_js = re.sub(r'\bjavascript\b', '', jd, flags=re.IGNORECASE)
    # Strip 'typescript' before checking for plain 'type' (edge case)
    jd_no_ts = re.sub(r'\btypescript\b', '', jd, flags=re.IGNORECASE)

    recognized: Set[str] = set()
    unassessed: Set[str] = set()

    for canonical, patterns in _LANG_PATTERNS:
        # Use de-polluted text only for the ambiguous languages
        search_text = jd_no_js if canonical == "Java" else jd
        for pat in patterns:
            if pat.search(search_text):
                recognized.add(canonical)
                break

    for kw, pat in _NON_LANG_PATTERNS:
        if pat.search(jd):
            unassessed.add(kw)

    # Prevent language names from leaking into unassessed
    recognized_lower = {l.lower() for l in recognized}
    unassessed = {u for u in unassessed if u.lower() not in recognized_lower}

    return sorted(recognized), sorted(unassessed)


# ─── Repository language retrieval ───────────────────────────────────────────

def get_repo_languages(db: Session, user: User) -> Set[str]:
    """Return distinct lowercase primary languages from cached repositories."""
    rows = (
        db.query(Repository.language)
        .filter(Repository.user_id == user.id, Repository.language.isnot(None))
        .all()
    )
    return {r.language.strip().lower() for r in rows if r.language and r.language.strip()}


# ─── Match calculation ────────────────────────────────────────────────────────

def calculate_match(
    recognized_languages: List[str],
    repo_languages: Set[str],
) -> Dict[str, Any]:
    """
    Compare required languages (from JD) against cached repo languages.
    Formula:  match_percentage = len(matched) / len(required) × 100
    """
    if not recognized_languages:
        return {
            "match_percentage": None,
            "matched_languages": [],
            "unmatched_languages": [],
            "message": (
                "No recognized programming languages were found in the job description. "
                "Try including specific language names (Python, Java, Go…)."
            ),
        }

    matched, unmatched = [], []
    for lang in recognized_languages:
        if lang.lower() in repo_languages:
            matched.append(lang)
        else:
            unmatched.append(lang)

    pct = round(len(matched) / len(recognized_languages) * 100, 2)
    return {
        "match_percentage": pct,
        "matched_languages": matched,
        "unmatched_languages": unmatched,
        "message": "Match based on primary languages in cached repositories.",
    }


# ─── Full Vibe Check pipeline ─────────────────────────────────────────────────

def analyze_compatibility(
    db: Session,
    user: User,
    job_description: str,
) -> CompatibilityAnalysis:
    """Full Vibe Check: extract → compare → persist → return."""
    if db.query(Repository).filter(Repository.user_id == user.id).count() == 0:
        raise ValueError(
            "No cached repositories found for this user. "
            "Please sync the GitHub profile first."
        )

    recognized, unassessed = extract_languages_from_jd(job_description)
    repo_langs = get_repo_languages(db, user)
    result = calculate_match(recognized, repo_langs)

    analysis = CompatibilityAnalysis(
        user_id=user.id,
        job_description=job_description,
        match_percentage=result["match_percentage"],
        recognized_required_languages=recognized,
        matched_languages=result["matched_languages"],
        unmatched_languages=result["unmatched_languages"],
        unassessed_keywords=list(unassessed),
        score_basis="distinct_primary_languages_in_cached_repositories",
        analyzed_at=utcnow(),
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    return analysis
