from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    pass


engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False},
    echo=False,
)


# Enable SQLite foreign-key enforcement on every connection
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """FastAPI dependency that yields a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables if they do not yet exist."""
    # Import models so Base.metadata is populated
    from app.models import models  # noqa: F401
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized.")
