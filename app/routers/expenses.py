from datetime import date
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.database.connection import get_db
from app.models import Expense, Subcategory, PaymentMethod, Establishment
from app.schemas.expense import ExpenseCreate, ExpenseRead, ExpenseUpdate

router = APIRouter(prefix="/api/expenses", tags=["expenses"])


def _base_query():
    return select(Expense).options(joinedload(Expense.subcategory).joinedload(Subcategory.category), joinedload(Expense.payment_method))


@router.get("", response_model=list[ExpenseRead])
def get_expenses(
    start_date: date | None = None,
    end_date: date | None = None,
    subcategory_id: list[UUID] | None = Query(default=None),
    payment_method_id: list[UUID] | None = Query(default=None),
    establishment_id: list[UUID] | None = Query(default=None),
    min_cents: int | None = Query(default=None, ge=0),
    max_cents: int | None = Query(default=None, ge=0),
    search: str | None = None,
    db: Session = Depends(get_db),
):
    query = _base_query()
    if start_date:
        query = query.where(Expense.expense_date >= start_date)
    if end_date:
        query = query.where(Expense.expense_date <= end_date)
    if subcategory_id:
        query = query.where(Expense.subcategory_id.in_(subcategory_id))
    if payment_method_id:
        query = query.where(Expense.payment_method_id.in_(payment_method_id))
    if establishment_id:
        query = query.where(Expense.establishment_id.in_(establishment_id))
    if min_cents is not None:
        query = query.where(Expense.amount_cents >= min_cents)
    if max_cents is not None:
        query = query.where(Expense.amount_cents <= max_cents)
    if search:
        query = query.where(Expense.description.ilike(f"%{search.strip()}%"))
    return list(db.scalars(query.order_by(Expense.expense_date.desc(), Expense.created_at.desc())))


@router.post("", response_model=ExpenseRead, status_code=status.HTTP_201_CREATED)
def post_expense(payload: ExpenseCreate, db: Session = Depends(get_db)):
    if not db.get(Subcategory, payload.subcategory_id):
        raise HTTPException(422, "Subcategoria não encontrada.")
    method = db.get(PaymentMethod, payload.payment_method_id)
    if not method or not method.is_active:
        raise HTTPException(422, "Forma de pagamento inválida ou inativa.")
    values = payload.model_dump()
    values["description"] = payload.description.strip()
    expense = Expense(**values)
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense


@router.patch("/{expense_id}", response_model=ExpenseRead)
def patch_expense(expense_id: UUID, payload: ExpenseUpdate, db: Session = Depends(get_db)):
    expense = db.get(Expense, expense_id)
    if not expense:
        raise HTTPException(404, "Despesa não encontrada.")
    changes = payload.model_dump(exclude_unset=True)
    if "subcategory_id" in changes and not db.get(Subcategory, changes["subcategory_id"]):
        raise HTTPException(422, "Subcategoria não encontrada.")
    if "payment_method_id" in changes:
        method = db.get(PaymentMethod, changes["payment_method_id"])
        if not method or not method.is_active:
            raise HTTPException(422, "Forma de pagamento inválida ou inativa.")
    for field, value in changes.items():
        setattr(expense, field, value.strip() if field == "description" and value else value)
    db.commit()
    return db.scalar(_base_query().where(Expense.id == expense_id))


@router.delete("/{expense_id}", status_code=204)
def delete_expense(expense_id: UUID, db: Session = Depends(get_db)):
    expense = db.get(Expense, expense_id)
    if not expense:
        raise HTTPException(404, "Despesa não encontrada.")
    db.delete(expense)
    db.commit()
