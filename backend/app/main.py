"""
FastAPI application entry point.

Startup: initializes SQLite database tables.
CORS: configured for the React frontend origin.
API: mounted under /api/v1 via the central router.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.config import settings
from app.database import init_db

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(name)s | %(message)s")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize the database on startup."""
    logger.info("Initializing database...")
    init_db()
    logger.info("Database ready. Starting GitHub Developer Portfolio API.")
    yield
    logger.info("Application shutting down.")


app = FastAPI(
    title="GitHub Developer Portfolio API",
    description=(
        "Backend API for the GitHub Developer Portfolio. "
        "Fetches GitHub profile/repository data, caches it in SQLite, "
        "runs Vibe Check compatibility analysis, and integrates DeepWiki MCP."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS — allow the React frontend and any localhost dev origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.frontend_url,
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/health", tags=["Health"])
async def health_check():
    """Simple health-check endpoint."""
    return {"status": "healthy", "service": "GitHub Developer Portfolio API", "version": "1.0.0"}
