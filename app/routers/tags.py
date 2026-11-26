from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.tag import Tag
from app.schemas.tag import TagCreate, TagRead

router = APIRouter(prefix="/api/tags", tags=["tags"])


@router.get("", response_model=list[TagRead])
def list_tags(db: Session = Depends(get_db)):
    return list(db.scalars(select(Tag).order_by(Tag.name)))


@router.post("", response_model=TagRead, status_code=status.HTTP_201_CREATED)
def create_tag(payload: TagCreate, db: Session = Depends(get_db)):
    name = payload.name.strip()
    if not name:
        raise HTTPException(422, "Informe um nome para a etiqueta.")
    normalized = name.casefold()
    existing = db.scalar(select(Tag).where(Tag.normalized_name == normalized))
    if existing:
        return existing
    tag = Tag(name=name, normalized_name=normalized)
    db.add(tag)
    try:
        db.commit()
    except Exception:
        db.rollback()
        existing = db.scalar(select(Tag).where(Tag.normalized_name == normalized))
        if existing:
            return existing
        raise
    db.refresh(tag)
    return tag
