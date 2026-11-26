from datetime import date
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.database.connection import get_db
from app.models import Expense, Subcategory, PaymentMethod, Establishment, Tag
from app.schemas.expense import ExpenseCreate, ExpenseRead, ExpenseUpdate

router = APIRouter(prefix="/api/expenses", tags=["expenses"])


def _base_query():
    return select(Expense).options(joinedload(Expense.subcategory).joinedload(Subcategory.category), joinedload(Expense.payment_method), joinedload(Expense.establishment), selectinload(Expense.tags))


def _resolve_tags(db: Session, names: list[str]) -> list[Tag]:
    resolved: list[Tag] = []
    seen: set[str] = set()
    for raw_name in names:
        name = raw_name.strip()
        if not name:
            continue
        normalized = name.casefold()
        if normalized in seen:
            continue
        seen.add(normalized)
        tag = db.scalar(select(Tag).where(Tag.normalized_name == normalized))
        if tag is None:
            tag = Tag(name=name, normalized_name=normalized)
            db.add(tag)
            db.flush()
        resolved.append(tag)
    if len(resolved) > 10:
        raise HTTPException(422, "Cada despesa pode ter no máximo 10 etiquetas.")
    return resolved


@router.get("")
def get_expenses(
    start_date: date | None = None,
    end_date: date | None = None,
    category_id: list[UUID] | None = Query(default=None),
    subcategory_id: list[UUID] | None = Query(default=None),
    tag_id: list[UUID] | None = Query(default=None),
    payment_method_id: list[UUID] | None = Query(default=None),
    establishment_id: list[UUID] | None = Query(default=None),
    min_cents: int | None = Query(default=None, ge=0),
    max_cents: int | None = Query(default=None, ge=0),
    search: str | None = None,
    limit: int = Query(default=200, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    query = _base_query()
    if start_date:
        query = query.where(Expense.expense_date >= start_date)
    if end_date:
        query = query.where(Expense.expense_date <= end_date)
    if category_id:
        query = query.join(Expense.subcategory).where(Subcategory.category_id.in_(category_id))
    if subcategory_id:
        query = query.where(Expense.subcategory_id.in_(subcategory_id))
    if tag_id:
        query = query.where(Expense.tags.any(Tag.id.in_(tag_id)))
    if payment_method_id:
        query = query.where(Expense.payment_method_id.in_(payment_method_id))
    if establishment_id:
        query = query.where(Expense.establishment_id.in_(establishment_id))
    if min_cents is not None:
        query = query.where(Expense.amount_cents >= min_cents)
    if max_cents is not None:
        query = query.where(Expense.amount_cents <= max_cents)
    if search and search.strip():
        query = query.where(Expense.description.ilike(f"%{search.strip()}%"))

    expenses = list(db.scalars(
        query.order_by(Expense.expense_date.desc(), Expense.created_at.desc())
        .offset(offset).limit(limit)
    ).unique())
    return [
        {
            "id": str(item.id),
            "description": item.description,
            "amount_cents": item.amount_cents,
            "expense_date": item.expense_date.isoformat(),
            "subcategory_id": str(item.subcategory_id),
            "subcategory": item.subcategory.name,
            "category_id": str(item.subcategory.category_id),
            "category": item.subcategory.category.name,
            "category_color": item.subcategory.category.color,
            "establishment_id": str(item.establishment_id),
            "establishment": item.establishment.name,
            "payment_method_id": str(item.payment_method_id),
            "payment_method": item.payment_method.name,
            "notes": item.notes,
            "tags": [{"id": str(tag.id), "name": tag.name} for tag in item.tags],
        }
        for item in expenses
    ]


@router.post("", response_model=ExpenseRead, status_code=status.HTTP_201_CREATED)
def post_expense(payload: ExpenseCreate, db: Session = Depends(get_db)):
    if not db.get(Subcategory, payload.subcategory_id):
        raise HTTPException(422, "Subcategoria não encontrada.")
    method = db.get(PaymentMethod, payload.payment_method_id)
    if not method or not method.is_active:
        raise HTTPException(422, "Forma de pagamento inválida ou inativa.")
    values = payload.model_dump(exclude={"tag_names"})
    values["description"] = payload.description.strip()
    expense = Expense(**values)
    expense.tags = _resolve_tags(db, payload.tag_names)
    db.add(expense)
    db.commit()
    return db.scalar(_base_query().where(Expense.id == expense.id))


@router.patch("/{expense_id}", response_model=ExpenseRead)
def patch_expense(expense_id: UUID, payload: ExpenseUpdate, db: Session = Depends(get_db)):
    expense = db.get(Expense, expense_id)
    if not expense:
        raise HTTPException(404, "Despesa não encontrada.")
    changes = payload.model_dump(exclude_unset=True)
    tag_names = changes.pop("tag_names", None)
    if "subcategory_id" in changes and not db.get(Subcategory, changes["subcategory_id"]):
        raise HTTPException(422, "Subcategoria não encontrada.")
    if "payment_method_id" in changes:
        method = db.get(PaymentMethod, changes["payment_method_id"])
        if not method or not method.is_active:
            raise HTTPException(422, "Forma de pagamento inválida ou inativa.")
    for field, value in changes.items():
        setattr(expense, field, value.strip() if field == "description" and value else value)
    if tag_names is not None:
        expense.tags = _resolve_tags(db, tag_names)
    db.commit()
    return db.scalar(_base_query().where(Expense.id == expense_id))


@router.delete("/{expense_id}", status_code=204)
def delete_expense(expense_id: UUID, db: Session = Depends(get_db)):
    expense = db.get(Expense, expense_id)
    if not expense:
        raise HTTPException(404, "Despesa não encontrada.")
    db.delete(expense)
    db.commit()
