"""SQLAlchemy engine and session factory."""

from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import get_database_url


class Base(DeclarativeBase):
    """Base class for SQLAlchemy models."""


@lru_cache(maxsize=1)
def get_engine():
    """Create the engine only when database access is first requested."""
    return create_engine(
        get_database_url(),
        pool_pre_ping=True,
        pool_recycle=300,
        connect_args={"connect_timeout": 10},
    )


def get_session_factory():
    return sessionmaker(
        bind=get_engine(),
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )


def get_db():
    """Yield a database session and always close it."""
    db = get_session_factory()()
    try:
        yield db
    finally:
        db.close()
