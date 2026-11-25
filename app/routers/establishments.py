from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models import Establishment
from app.schemas.establishment import EstablishmentCreate, EstablishmentRead

router = APIRouter(prefix="/api/establishments", tags=["establishments"])


@router.get("", response_model=list[EstablishmentRead])
def get_establishments(db: Session = Depends(get_db)):
    return list(db.scalars(select(Establishment).order_by(func.lower(Establishment.name))))


@router.post("", response_model=EstablishmentRead, status_code=status.HTTP_201_CREATED)
def post_establishment(payload: EstablishmentCreate, db: Session = Depends(get_db)):
    name = payload.name.strip()
    if not name:
        raise HTTPException(422, "Informe o nome do estabelecimento.")

    normalized_name = name.casefold()
    existing = db.scalar(select(Establishment).where(Establishment.normalized_name == normalized_name))
    if existing:
        return existing

    establishment = Establishment(name=name, normalized_name=normalized_name)
    db.add(establishment)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        existing = db.scalar(select(Establishment).where(Establishment.normalized_name == normalized_name))
        if existing:
            return existing
        raise HTTPException(409, "Não foi possível cadastrar o estabelecimento.") from exc
    db.refresh(establishment)
    return establishment
