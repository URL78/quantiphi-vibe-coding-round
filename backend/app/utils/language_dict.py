"""
Programming language alias dictionary for Vibe Check language extraction.

Design decisions:
  - Canonical name uses the most common human-readable form (e.g. "C++", "JavaScript").
  - Aliases are all lowercase; matching is case-insensitive.
  - Patterns use word-boundary regex to prevent substring matches.
  - Languages ordered from most specific to least to avoid false positives
    (C++ and C# must be checked before standalone C).
  - Non-language technology keywords are in NON_LANGUAGE_KEYWORDS;
    they appear in job descriptions but are NOT counted as matched languages.
"""

from typing import Dict, List

# (canonical_name, [aliases]) — order matters: more specific entries first
LANGUAGE_DEFINITIONS: List[tuple] = [
    # Multi-char / symbol names first to avoid C being picked up inside them
    ("C++",          ["c\\+\\+", "cpp"]),
    ("C#",           ["c#", "csharp", "c sharp"]),
    ("Objective-C",  ["objective-c", "objc", "objective c"]),

    # Single-letter last to avoid false matches
    ("C",            ["\\bc(?![+#\\w])"]),   # handled specially in extractor

    # Popular languages
    ("Python",       ["python"]),
    ("JavaScript",   ["javascript", "js", "ecmascript"]),
    ("TypeScript",   ["typescript"]),
    ("Java",         ["java(?!script)"]),     # avoid matching 'javascript'
    ("Go",           ["golang", "\\bgo\\b"]),
    ("Rust",         ["rust"]),
    ("Ruby",         ["ruby"]),
    ("PHP",          ["php"]),
    ("Kotlin",       ["kotlin"]),
    ("Swift",        ["swift"]),
    ("Dart",         ["dart"]),
    ("Scala",        ["scala"]),
    ("R",            ["\\br\\b(?! language)"]),  # careful — just "R" is tricky
    ("Shell",        ["shell script", "bash", "\\bsh\\b"]),
    ("HTML",         ["html5?", "html"]),
    ("CSS",          ["css3?", "\\bcss\\b"]),
    ("SQL",          ["\\bsql\\b"]),
    ("Perl",         ["perl"]),
    ("Haskell",      ["haskell"]),
    ("Elixir",       ["elixir"]),
    ("Clojure",      ["clojure"]),
    ("Lua",          ["lua"]),
    ("MATLAB",       ["matlab"]),
    ("Julia",        ["julia"]),
    ("Assembly",     ["assembly", "\\basm\\b"]),
    ("Groovy",       ["groovy"]),
    ("Erlang",       ["erlang"]),
    ("F#",           ["f#", "fsharp"]),
    ("Solidity",     ["solidity"]),
    ("COBOL",        ["cobol"]),
    ("Fortran",      ["fortran"]),
    ("Ada",          ["\\bada\\b"]),
    ("Zig",          ["\\bzig\\b"]),
    ("Nim",          ["\\bnim\\b"]),
]

# Canonical names in their proper display casing
CANONICAL_NAMES: Dict[str, str] = {
    name.lower(): name for name, _ in LANGUAGE_DEFINITIONS
}

# Non-language technical keywords — returned as unassessed_keywords
# These must NOT count as matched programming languages
NON_LANGUAGE_KEYWORDS = {
    # Frameworks / Libraries
    "fastapi", "django", "flask", "express", "nestjs", "spring boot", "spring",
    "rails", "laravel", "next.js", "nextjs", "nuxt", "vue", "react", "angular",
    "svelte", "remix", "astro", "htmx", "jquery", "bootstrap", "tailwind",
    "tensorflow", "pytorch", "keras", "scikit-learn", "sklearn", "pandas",
    "numpy", "langchain", "langgraph", "hugging face", "huggingface",
    "node.js", "nodejs", "deno", "bun",
    # Cloud/Infra
    "aws", "gcp", "azure", "google cloud", "digitalocean", "heroku",
    "docker", "kubernetes", "k8s", "terraform", "ansible", "pulumi",
    "serverless", "lambda", "fargate", "ec2", "s3", "rds",
    # Databases
    "postgresql", "postgres", "mysql", "mariadb", "sqlite", "oracle",
    "mongodb", "redis", "elasticsearch", "cassandra", "dynamodb",
    "neo4j", "influxdb", "clickhouse", "snowflake", "bigquery",
    # Messaging / Streaming
    "kafka", "rabbitmq", "sqs", "pubsub", "nats", "celery",
    # DevOps / CI/CD
    "jenkins", "github actions", "gitlab ci", "circleci", "travis ci",
    "git", "github", "gitlab", "bitbucket", "jira", "confluence",
    "linux", "unix", "macos", "windows server",
    # API / Auth / Protocols
    "rest", "restful", "graphql", "grpc", "websocket", "mqtt",
    "oauth", "jwt", "openid", "saml", "ldap",
    "http", "https", "tcp/ip", "ssl", "tls",
    # Architecture / Practices
    "microservices", "monolith", "event-driven", "ci/cd", "devops", "mlops",
    "agile", "scrum", "kanban", "tdd", "bdd",
    # Machine Learning / AI
    "machine learning", "deep learning", "nlp", "computer vision",
    "llm", "rag", "vector database", "embedding",
}
