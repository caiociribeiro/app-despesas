from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models import PaymentMethod
from app.schemas.payment_method import PaymentMethodCreate, PaymentMethodRead

router = APIRouter(prefix="/api/payment-methods", tags=["payment methods"])


@router.get("", response_model=list[PaymentMethodRead])
def get_payment_methods(db: Session = Depends(get_db)):
    return list(db.scalars(select(PaymentMethod).where(PaymentMethod.is_active.is_(True)).order_by(PaymentMethod.name)))


@router.post("", response_model=PaymentMethodRead, status_code=201)
def post_payment_method(payload: PaymentMethodCreate, db: Session = Depends(get_db)):
    method = PaymentMethod(name=payload.name.strip())
    db.add(method)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(409, "Essa forma de pagamento já existe.") from exc
    db.refresh(method)
    return method
