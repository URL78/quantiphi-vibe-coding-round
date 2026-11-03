"""
Rule-based career recommendation service.

Generates deterministic suggestions from unmatched language gaps revealed
by a Vibe Check analysis. No external LLM is used.

Suggestions are labelled as recommendations, not verified facts.
"""

from typing import Any, Dict, List

from app.models.models import CompatibilityAnalysis

# Suggestion templates per language (fallback to a generic template)
_LANGUAGE_TIPS: Dict[str, str] = {
    "Python": (
        "Build or feature a Python project on GitHub — e.g. a CLI tool, "
        "REST API with FastAPI/Flask, or a data analysis script."
    ),
    "JavaScript": (
        "Add a JavaScript project — a web app, browser extension, or "
        "Node.js utility can demonstrate JS proficiency."
    ),
    "TypeScript": (
        "Convert an existing JavaScript project to TypeScript or start a new "
        "TypeScript codebase to demonstrate type-safe JS development."
    ),
    "Java": (
        "Consider building a Spring Boot REST API or a Java CLI application "
        "to provide evidence of Java experience."
    ),
    "C++": (
        "Feature a C++ project — systems programming, competitive-programming "
        "solutions, or an embedded/performance-critical application."
    ),
    "C": (
        "A C project like a data-structures library, OS-level utility, or "
        "embedded firmware sample would demonstrate C proficiency."
    ),
    "C#": (
        "Add a .NET/C# project — an ASP.NET Core API, Unity game prototype, "
        "or WPF desktop application."
    ),
    "Go": (
        "Build a Go CLI tool, HTTP microservice, or concurrency-focused utility "
        "to demonstrate Golang skills."
    ),
    "Rust": (
        "A Rust project (CLI tool, WebAssembly module, or systems utility) "
        "would strengthen your portfolio for roles requiring Rust."
    ),
    "Ruby": (
        "Add a Ruby on Rails application or a standalone Ruby script/gem "
        "to evidence Ruby development experience."
    ),
    "PHP": (
        "Feature a PHP project such as a Laravel or Symfony web application."
    ),
    "Kotlin": (
        "Build a Kotlin Android app or a Kotlin-based JVM service to "
        "show Kotlin proficiency."
    ),
    "Swift": (
        "Add an iOS or macOS app in Swift to demonstrate Apple platform development."
    ),
    "Scala": (
        "A Scala project — Akka actor application, Spark job, or functional "
        "programming exercise — would address this gap."
    ),
    "R": (
        "An R project (data analysis notebook, statistical model, "
        "or Shiny dashboard) would demonstrate R usage."
    ),
}

_GENERIC_TEMPLATE = (
    "Your public repositories currently provide limited evidence of {lang} usage. "
    "Consider building a project that uses {lang} to improve your portfolio alignment."
)


def _generate_suggestion(lang: str) -> str:
    return _LANGUAGE_TIPS.get(lang, _GENERIC_TEMPLATE.format(lang=lang))


def get_recommendations(analysis: CompatibilityAnalysis) -> List[Dict[str, Any]]:
    """
    Generate a list of {skill, suggestion} recommendations
    based on the unmatched languages in a Vibe Check analysis.
    """
    recommendations: List[Dict[str, Any]] = []

    for lang in analysis.unmatched_languages or []:
        recommendations.append(
            {
                "skill": lang,
                "suggestion": _generate_suggestion(lang),
            }
        )

    return recommendations
