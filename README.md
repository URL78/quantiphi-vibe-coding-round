# GitHub Developer Portfolio

An AI-assisted developer portfolio backend that turns public GitHub data into profile analytics, repository insights, and job-description compatibility results. The service is built with FastAPI and SQLite, with GitHub REST/GraphQL integrations and an optional DeepWiki MCP integration.

> This repository currently contains the backend and project documentation. A frontend is described in the product requirements but is not included here.

## Features

- Synchronize public GitHub profiles and repositories.
- Cache profile and repository data in SQLite.
- Provide profile analytics, contribution data, repository lists, and language distribution.
- Compare recognized programming languages in a job description against cached repository languages.
- Provide portfolio, career recommendation, interview-preparation, and DeepWiki API routes.
- Expose interactive OpenAPI documentation through FastAPI.

## Requirements

- Python 3.10 or later
- GitHub token is optional. Configure one to access higher GitHub API rate limits.
- SQLite is used by default; no separate database server is required.

## Run Locally

From the repository root, create and activate a virtual environment, install dependencies, and start the API:

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload
```

If PowerShell prevents virtual environment activation, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in that terminal and activate again. On macOS or Linux, activate with `source .venv/bin/activate` instead.

The API is available at:

- Health check: <http://127.0.0.1:8000/health>
- OpenAPI UI: <http://127.0.0.1:8000/docs>
- ReDoc: <http://127.0.0.1:8000/redoc>
- API base path: `/api/v1`

The application initializes its SQLite tables on startup. By default, the database is `backend/portfolio.db` when launched from the `backend` directory.

## Configuration

Copy `backend/.env.example` to `backend/.env` and set values as needed:

| Variable | Purpose | Default |
|---|---|---|
| `GITHUB_TOKEN` | Optional GitHub personal access token for higher API limits | Unset |
| `DATABASE_URL` | SQLAlchemy database URL | `sqlite:///./portfolio.db` |
| `DEEPWIKI_MCP_URL` | DeepWiki MCP server endpoint | `https://mcp.deepwiki.com/mcp` |
| `FRONTEND_URL` | Allowed frontend origin for CORS | `http://localhost:5173` |
| `PROFILE_CACHE_TTL` | Profile cache lifetime in seconds | `3600` |
| `REPO_CACHE_TTL` | Repository cache lifetime in seconds | `3600` |
| `CONTRIBUTION_CACHE_TTL` | Contribution cache lifetime in seconds | `21600` |

Keep secrets in your local `.env`; do not commit them. The real `.env` file is excluded by `.gitignore`.

## Tests

Run the backend tests from the `backend` directory:

```powershell
pytest
```

The test suite uses a test database and mocks external service calls so tests do not require live GitHub or DeepWiki access.

## Project Layout

```text
backend/
  app/
    api/             FastAPI endpoint routers
    integrations/    External service integrations
    models/          SQLAlchemy models
    schemas/         Pydantic schemas
    services/        Application and cache logic
    utils/           Shared utilities and language data
  alembic/           Database migration configuration
  tests/             Backend tests
docs/                Requirements, API, and database documentation
UML diagrams/        Project diagrams
```

## Documentation

- [Requirements](docs/REQUIREMENTS.md)
- [API documentation](docs/API_DOCUMENTATION.md)
- [Database schema](docs/DATABASE_SCHEMA.md)

## API Overview

The API is mounted at `/api/v1`. It includes routes for profile synchronization, analytics, contributions, repositories, compatibility analysis, career recommendations, portfolio settings, interview preparation, and DeepWiki. See the interactive `/docs` page while the server is running for the exact request and response schemas.
