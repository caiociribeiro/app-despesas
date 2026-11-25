"""Application configuration loaded from environment variables."""

import os
from dotenv import load_dotenv

load_dotenv()

APP_NAME = os.getenv("APP_NAME", "AppDespesas")
APP_ENV = os.getenv("APP_ENV", "development")
DATABASE_URL = os.getenv("DATABASE_URL", "").strip()


def get_database_url() -> str:
    """Return a SQLAlchemy URL using psycopg 3.

    Neon commonly supplies a URL beginning with ``postgresql://``.
    SQLAlchemy is explicitly directed to use the installed psycopg driver.
    """
    if not DATABASE_URL:
        raise RuntimeError(
            "DATABASE_URL não configurada. Adicione a connection string do Neon ao arquivo .env."
        )

    if DATABASE_URL.startswith("postgres://"):
        return DATABASE_URL.replace("postgres://", "postgresql+psycopg://", 1)
    if DATABASE_URL.startswith("postgresql://"):
        return DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)
    if DATABASE_URL.startswith("postgresql+psycopg://"):
        return DATABASE_URL

    raise RuntimeError(
        "DATABASE_URL deve começar com postgres://, postgresql:// ou postgresql+psycopg://."
    )
