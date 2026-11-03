"""
Pytest configuration and shared fixtures.
Mocks external services so tests never call real GitHub or DeepWiki APIs.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app

# Use an in-memory SQLite database for tests
TEST_DATABASE_URL = "sqlite:///./test_portfolio.db"

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Create all tables before tests, drop after."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db():
    """Yield a test database session."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        db.close()


@pytest.fixture
def client(db):
    """FastAPI test client wired to the test database."""
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
