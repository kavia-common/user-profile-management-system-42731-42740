import os
from dataclasses import dataclass

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, scoped_session, sessionmaker


Base = declarative_base()


@dataclass(frozen=True)
class DbConfig:
    """Runtime database configuration.

    Uses DATABASE_URL if provided, otherwise defaults to a local SQLite file.
    """

    database_url: str


def _default_db_url() -> str:
    """Return a safe default SQLite database URL."""
    # Keep DB inside container folder to work in preview and local runs.
    # This path is resolved by SQLAlchemy (sqlite:///relative/path.db).
    return "sqlite:///./users.db"


# Singleton engine/session factory for a lightweight app.
_db_config = DbConfig(database_url=os.getenv("DATABASE_URL", _default_db_url()))
engine = create_engine(
    _db_config.database_url,
    connect_args={"check_same_thread": False} if _db_config.database_url.startswith("sqlite") else {},
    future=True,
)
SessionLocal = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)
)


def init_db() -> None:
    """Create tables if they do not exist."""
    # Import models to ensure metadata is registered
    from . import models  # noqa: F401

    Base.metadata.create_all(bind=engine)


def get_db_session():
    """Context manager-like generator for getting a session.

    Intended for use in request handlers; ensures commit/rollback/close.
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
