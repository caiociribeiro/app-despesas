from fastapi import APIRouter, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.database.connection import get_engine

router = APIRouter(tags=["health"])


@router.get("/health")
def health():
    """Check whether the local API process is responding."""
    return {"status": "ok", "service": "appdespesas"}


@router.get("/health/db")
def database_health():
    """Check connectivity to the configured PostgreSQL database."""
    try:
        with get_engine().connect() as connection:
            connection.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=503,
            detail="Não foi possível conectar ao banco PostgreSQL.",
        ) from exc
