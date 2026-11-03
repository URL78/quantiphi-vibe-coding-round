# GitHub Developer Portfolio — API Documentation

**Base path:** `/api/v1`  
**Backend:** FastAPI  
**API style:** REST/JSON  
**Purpose:** Contract between React frontend and FastAPI backend.

## 1. API conventions

### 1.1 General rules

- Frontend calls only the FastAPI backend.
- GitHub REST/GraphQL and DeepWiki MCP calls happen server-side.
- JSON request and response bodies use `snake_case`.
- Use appropriate HTTP status codes.
- Validate inputs with Pydantic.
- Do not return stack traces or secrets.
- Use a consistent error shape.

Example error:

```json
{
  "detail": {
    "code": "GITHUB_USER_NOT_FOUND",
    "message": "No public GitHub profile was found for this username."
  }
}
```

### 1.2 Suggested status codes

| Status | Meaning |
|---|---|
| 200 | Successful read/action |
| 201 | Resource created |
| 400 | Invalid request or business rule |
| 404 | User/repository/analysis not found |
| 422 | Request validation failed |
| 429 | Upstream rate limit or request throttling |
| 502 | External service returned an invalid/failed response |
| 503 | External service temporarily unavailable |

### 1.3 Common query parameters

Repository list:
- `sort_by`: `stars`, `updated_at`, or `name`
- `order`: `asc` or `desc`
- `page`: positive integer, default 1
- `limit`: positive integer, default 10; cap to a reasonable maximum

## 2. Profile and synchronization

### POST `/profile/sync`

Synchronize a public GitHub profile and its repositories. Check cache first unless forced refresh is requested.

Request:

```json
{
  "username": "octocat",
  "force_refresh": false
}
```

Response:

```json
{
  "success": true,
  "username": "octocat",
  "message": "Profile synchronized successfully.",
  "cache_status": "miss",
  "last_synced_at": "2026-11-03T10:30:00Z"
}
```

Behavior:
- Validate username.
- Fetch profile and repositories from GitHub when cache is absent/expired or refresh is forced.
- Normalize and upsert records.
- Do not delete existing good cache if the upstream refresh fails.
- A successful cache-only response may use `cache_status: "hit"`.

### GET `/profile/{username}`

Return cached profile details.

Example response:

```json
{
  "id": 1,
  "github_username": "octocat",
  "name": "The Octocat",
  "bio": null,
  "avatar_url": "https://avatars.githubusercontent.com/u/583231",
  "github_url": "https://github.com/octocat",
  "followers": 100,
  "following": 10,
  "public_repos": 8,
  "total_stars": 250,
  "total_forks": 40,
  "last_synced_at": "2026-11-03T10:30:00Z",
  "is_stale": false
}
```

### POST `/profile/{username}/refresh`

Force refresh profile and repository data. Equivalent to synchronization with `force_refresh: true`.

## 3. Dashboard analytics

### GET `/analytics/{username}`

Return aggregate profile statistics.

Example response:

```json
{
  "username": "octocat",
  "followers": 100,
  "following": 10,
  "public_repos": 8,
  "total_stars": 250,
  "total_forks": 40,
  "total_contributions": 850,
  "is_stale": false
}
```

### GET `/analytics/{username}/languages`

Return primary-language distribution across cached repositories.

Example response:

```json
{
  "username": "octocat",
  "basis": "repository_count",
  "languages": [
    {
      "name": "Python",
      "repository_count": 5,
      "percentage": 62.5
    },
    {
      "name": "JavaScript",
      "repository_count": 3,
      "percentage": 37.5
    }
  ]
}
```

Do not describe this as line-of-code distribution. Repositories with no detected primary language are excluded from the language denominator.

### GET `/contributions/{username}`

Return daily contribution calendar data.

Optional query parameters:
- `from`: ISO date
- `to`: ISO date

Example response:

```json
{
  "username": "octocat",
  "total_contributions": 850,
  "contributions": [
    {
      "date": "2026-11-01",
      "count": 5,
      "intensity": 3
    },
    {
      "date": "2026-11-02",
      "count": 0,
      "intensity": 0
    }
  ],
  "is_stale": false
}
```

### GET `/contributions/{username}/streaks`

Example response:

```json
{
  "username": "octocat",
  "current_streak": 4,
  "longest_streak": 18,
  "last_contribution_date": "2026-11-02"
}
```

Streak definitions must be consistent and calculated from actual daily contribution records. A zero-contribution day breaks a streak.

## 4. Repositories

### GET `/repositories/{username}`

Query parameters:
- `sort_by=stars|updated_at|name`
- `order=asc|desc`
- `page=1`
- `limit=10`

Example response:

```json
{
  "username": "octocat",
  "total": 8,
  "page": 1,
  "limit": 10,
  "repositories": [
    {
      "id": 101,
      "github_repo_id": 123456,
      "name": "project-alpha",
      "description": "Example backend application",
      "language": "Python",
      "stars": 25,
      "forks": 8,
      "html_url": "https://github.com/octocat/project-alpha",
      "is_fork": false,
      "updated_at": "2026-10-30T12:00:00Z",
      "featured": true
    }
  ]
}
```

### GET `/repositories/{username}/{repo_name}`

Return cached details for one repository belonging to the user.

### PATCH `/repositories/{username}/{repo_name}/featured`

Request:

```json
{
  "featured": true,
  "display_order": 1
}
```

Response:

```json
{
  "success": true,
  "repository": "project-alpha",
  "featured": true,
  "display_order": 1
}
```

The backend must verify that the repository belongs to the specified cached user.

## 5. Mandatory Tech Stack Compatibility / Vibe Check

This module implements the explicit Quantiphi requirement: input a job description, compare its language keywords against languages in the user's cached repositories, and show a Match Percentage badge at the top of the profile.

### POST `/compatibility/analyze`

Request:

```json
{
  "username": "octocat",
  "job_description": "We need a developer with Python, C++, JavaScript, FastAPI, Docker and PostgreSQL experience."
}
```

Expected behavior:
1. Validate job description.
2. Extract distinct recognized programming languages using a predefined dictionary.
3. Normalize aliases to canonical language names.
4. Read distinct primary languages from the user's cached repositories in SQLite.
5. Compare the two sets.
6. Calculate score on the backend.
7. Persist the analysis.
8. Return matched and unmatched languages.
9. Frontend displays the Match Percentage badge prominently at the top of the profile/dashboard.

Example response (illustrative):

```json
{
  "analysis_id": 12,
  "username": "octocat",
  "match_percentage": 66.67,
  "recognized_required_languages": [
    "Python",
    "C++",
    "JavaScript"
  ],
  "matched_languages": [
    "Python",
    "JavaScript"
  ],
  "unmatched_languages": [
    "C++"
  ],
  "unassessed_keywords": [
    "FastAPI",
    "Docker",
    "PostgreSQL"
  ],
  "score_basis": "distinct_primary_languages_in_cached_repositories",
  "message": "GitHub evidence-based compatibility estimate."
}
```

The sample score above is illustrative; calculate it from the actual input and cache. In production code, do not hardcode this example.

**Required formula:**

`match_percentage = matched_languages_count / recognized_required_languages_count * 100`

Use distinct canonical language names. If no recognized language is found, return `match_percentage: null` and a message such as `No recognized programming-language requirements were found.` Do not divide by zero.

If no cached repositories exist, return a clear response indicating that the user must synchronize GitHub data before analysis. Do not treat missing cache as proof of missing skills.

**Important:** Frameworks, databases, infrastructure tools, and platforms (e.g. FastAPI, Docker, PostgreSQL, Redis, Kubernetes) are not primary programming languages. They must not count as matched in this required language-only score. They may be returned as `unassessed_keywords`.

### GET `/compatibility/{analysis_id}`

Return a previously stored analysis, including matched/unmatched languages and score.

## 6. Career recommendations

### GET `/career/recommendations/{analysis_id}`

Return deterministic recommendations derived from unmatched recognized languages or other clearly identified gaps.

Example response:

```json
{
  "analysis_id": 12,
  "recommendations": [
    {
      "skill": "C++",
      "suggestion": "Build or feature a project demonstrating C++ development."
    }
  ]
}
```

Do not call an external LLM for this MVP module.

## 7. DeepWiki repository assistant

The frontend calls our FastAPI routes. FastAPI calls DeepWiki MCP using an MCP client. The MCP tool names are not REST paths.

### GET `/deepwiki/{owner}/{repo}/structure`

Retrieve documentation structure through DeepWiki's supported `read_wiki_structure` tool.

### GET `/deepwiki/{owner}/{repo}/contents`

Retrieve documentation contents through `read_wiki_contents`. If the tool requires arguments, pass the correct documented structure.

### POST `/deepwiki/{owner}/{repo}/ask`

Request:

```json
{
  "question": "Explain the architecture of this project."
}
```

Response:

```json
{
  "owner": "octocat",
  "repository": "project-alpha",
  "question": "Explain the architecture of this project.",
  "answer": "The repository documentation describes...",
  "source": "DeepWiki"
}
```

Implementation requirements:
- Use DeepWiki MCP tools such as `read_wiki_structure`, `read_wiki_contents`, and `ask_question`.
- Connect through the supported MCP transport/client.
- Do not invent a REST endpoint for the MCP tools.
- Handle unsupported/unindexed repositories and timeouts.
- Keep failures isolated to the AI section.

## 8. Interview preparation

### POST `/interview/generate`

Request:

```json
{
  "username": "octocat",
  "repository": "project-alpha",
  "difficulty": "medium",
  "number_of_questions": 5
}
```

Response:

```json
{
  "repository": "project-alpha",
  "questions": [
    "Explain the architecture described for this application.",
    "Why was the selected database used?"
  ]
}
```

Generate questions using available DeepWiki context. Validate difficulty and question count.

### POST `/interview/evaluate`

Request:

```json
{
  "owner": "octocat",
  "repository": "project-alpha",
  "question": "Why did you choose this architecture?",
  "answer": "It separates the API and data access layers."
}
```

Response:

```json
{
  "feedback": "Your answer identifies separation of concerns. You could improve it by explaining the responsibilities of each layer.",
  "strengths": [
    "Mentions separation of concerns"
  ],
  "improvements": [
    "Explain how the layers communicate"
  ],
  "context_available": true
}
```

Feedback must be grounded in available repository context. If DeepWiki cannot provide sufficient context, say so.

### POST `/interview/session` and GET `/interview/session/{session_id}`

These are optional. For the simplest MVP, keep mock interview progress in frontend state and omit persistent session APIs. Add these endpoints only if server-side session state is actually implemented.

## 9. Settings

### GET `/settings/{username}`

Example response:

```json
{
  "username": "octocat",
  "theme": "dark"
}
```

### PUT `/settings/{username}`

Request:

```json
{
  "theme": "dark"
}
```

For a no-login MVP, do not claim these username-associated settings are private or protected from other visitors.

## 10. Public portfolio

### GET `/portfolio/{username}`

Return a composed public response containing:
- Profile summary.
- Profile statistics.
- Contribution summary.
- Language distribution.
- Featured repositories.
- Latest compatibility analysis/badge, if one exists and is intended to be public.

Do not expose API credentials, internal cache metadata beyond safe freshness indicators, or private application data.

## 11. Suggested endpoint inventory

| Module | Endpoint count |
|---|---:|
| Profile and sync | 3 |
| Analytics and contributions | 4 |
| Repositories | 3 |
| Compatibility | 2 |
| Career recommendations | 1 |
| DeepWiki | 3 |
| Interview | 2 required; 2 optional session routes |
| Settings | 2 |
| Portfolio | 1 |

The endpoint list is a proposed implementation contract, not a requirement to create unnecessary routes. Consolidate routes if that makes the MVP simpler, but preserve all required behavior—especially the Vibe Check feature.
