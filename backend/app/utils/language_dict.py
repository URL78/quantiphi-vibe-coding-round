"""
Plain-text alias dictionary for Vibe Check language extraction.

Rules
─────
- Each alias is a PLAIN LOWERCASE STRING — no regex metacharacters.
  Word-boundary wrapping and re.escape are applied by compatibility_service.
- Order matters for disambiguation: list more-specific entries before
  generic ones (e.g. "javascript" before "java").
- Standalone "go" is too ambiguous as an English word; use "golang" or
  "go language" instead.
- "R" is too short and ambiguous; require "r language" or "r programming".
- NON_LANGUAGE_KEYWORDS are frameworks/tools/infra that appear in job
  descriptions but must NOT contribute to the language match score.
"""

from typing import Dict, List, Tuple

# (canonical_display_name, [plain_text_aliases…])
# JavaScript MUST come before Java.
LANGUAGE_DEFINITIONS: List[Tuple[str, List[str]]] = [
    # ── Specific / must-come-first ───────────────────────────────────────
    ("JavaScript",   ["javascript", "js", "ecmascript", "node.js", "nodejs"]),
    ("TypeScript",   ["typescript", "ts"]),
    ("C++",          ["c++", "cpp", "cplusplus"]),
    ("C#",           ["c#", "csharp", "c sharp"]),
    ("Objective-C",  ["objective-c", "objc"]),
    # ── After JavaScript so "java" in "javascript" is already stripped ───
    ("Java",         ["java"]),
    # ── Other languages ──────────────────────────────────────────────────
    ("Python",       ["python", "py"]),
    ("Go",           ["golang", "go language", "go programming", "go"]),
    ("Rust",         ["rust", "rust-lang"]),
    ("Ruby",         ["ruby", "ruby on rails"]),
    ("PHP",          ["php"]),
    ("Kotlin",       ["kotlin"]),
    ("Swift",        ["swift"]),
    ("Scala",        ["scala"]),
    ("Dart",         ["dart", "flutter"]),       # flutter → dart
    ("Shell",        ["bash", "shell script", "shell scripting", "zsh", "sh script"]),
    ("SQL",          ["sql", "pl/sql", "t-sql", "tsql"]),
    ("HTML",         ["html", "html5"]),
    ("CSS",          ["css", "css3"]),
    ("Perl",         ["perl"]),
    ("Haskell",      ["haskell"]),
    ("Elixir",       ["elixir"]),
    ("Erlang",       ["erlang"]),
    ("Clojure",      ["clojure"]),
    ("Lua",          ["lua"]),
    ("MATLAB",       ["matlab"]),
    ("Julia",        ["julia"]),
    ("Assembly",     ["assembly", "assembly language", "asm"]),
    ("Groovy",       ["groovy"]),
    ("Solidity",     ["solidity"]),
    ("COBOL",        ["cobol"]),
    ("Fortran",      ["fortran"]),
    ("F#",           ["f#", "fsharp"]),
    ("Zig",          ["zig"]),
    ("Nim",          ["nim"]),
    ("R",            ["r language", "r programming"]),  # 'R' alone is too ambiguous
]

# Canonical display names
CANONICAL_NAMES: Dict[str, str] = {
    name.lower(): name for name, _ in LANGUAGE_DEFINITIONS
}

# Non-language tech keywords → reported as unassessed (not scored)
NON_LANGUAGE_KEYWORDS = {
    # ── Web Frameworks ──────────────────────────────────────────────────
    "react", "angular", "vue", "svelte", "next.js", "nuxt", "remix",
    "django", "flask", "fastapi", "express", "nestjs", "spring", "spring boot",
    "rails", "laravel", "symfony", "asp.net", "htmx", "jquery", "bootstrap",
    "tailwind",
    # ── Runtime / Platforms ─────────────────────────────────────────────
    "node", "deno", "bun",
    # ── ML / AI ─────────────────────────────────────────────────────────
    "tensorflow", "pytorch", "keras", "scikit-learn", "sklearn",
    "pandas", "numpy", "langchain", "hugging face", "huggingface", "llm",
    "machine learning", "deep learning", "nlp", "computer vision",
    "rag", "vector database",
    # ── Cloud / Infra ────────────────────────────────────────────────────
    "aws", "gcp", "azure", "google cloud", "digitalocean", "heroku",
    "docker", "kubernetes", "k8s", "terraform", "ansible", "pulumi",
    "serverless", "lambda", "ec2", "s3", "rds", "fargate",
    # ── Databases ───────────────────────────────────────────────────────
    "postgresql", "postgres", "mysql", "mariadb", "sqlite", "oracle",
    "mongodb", "redis", "elasticsearch", "cassandra", "dynamodb",
    "neo4j", "influxdb", "clickhouse", "snowflake", "bigquery",
    # ── Messaging / Streaming ───────────────────────────────────────────
    "kafka", "rabbitmq", "sqs", "pubsub", "nats", "celery",
    # ── DevOps / CI/CD ──────────────────────────────────────────────────
    "jenkins", "github actions", "gitlab ci", "circleci", "travis ci",
    "git", "github", "gitlab", "bitbucket", "jira", "confluence",
    "linux", "unix",
    # ── API / Auth ───────────────────────────────────────────────────────
    "rest", "restful", "graphql", "grpc", "websocket", "oauth", "jwt",
    "openid", "saml",
    # ── Practices / Architecture ─────────────────────────────────────────
    "microservices", "event-driven", "ci/cd", "devops", "mlops",
    "agile", "scrum", "tdd", "bdd",
}
