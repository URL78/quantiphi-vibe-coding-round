from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # GitHub integration
    github_token: Optional[str] = None

    # Database
    database_url: str = "sqlite:///./portfolio.db"

    # DeepWiki MCP
    deepwiki_mcp_url: str = "https://mcp.deepwiki.com/mcp"

    # CORS
    frontend_url: str = "http://localhost:5173"

    # Cache TTLs (seconds)
    profile_cache_ttl: int = 3600       # 1 hour
    repo_cache_ttl: int = 3600          # 1 hour
    contribution_cache_ttl: int = 21600  # 6 hours

    # GitHub API
    github_api_base: str = "https://api.github.com"
    github_graphql_url: str = "https://api.github.com/graphql"

    # Request timeout (seconds)
    request_timeout: float = 15.0

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
