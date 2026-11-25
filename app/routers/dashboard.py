from datetime import date
from calendar import monthrange
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload
from fastapi import APIRouter, Depends

from app.database.connection import get_db
from app.models import Expense, Subcategory

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/monthly")
def monthly_summary(year: int | None = None, month: int | None = None, db: Session = Depends(get_db)):
    today = date.today()
    year = year or today.year
    month = month or today.month
    if month < 1 or month > 12:
        from fastapi import HTTPException
        raise HTTPException(422, "Mês deve estar entre 1 e 12.")
    start = date(year, month, 1)
    end = date(year, month, monthrange(year, month)[1])
    total = db.scalar(select(func.coalesce(func.sum(Expense.amount_cents), 0)).where(Expense.expense_date.between(start, end)))
    recent = db.scalars(
        select(Expense).options(joinedload(Expense.subcategory).joinedload(Subcategory.category), joinedload(Expense.establishment))
        .where(Expense.expense_date.between(start, end))
        .order_by(Expense.expense_date.desc(), Expense.created_at.desc()).limit(8)
    ).all()
    return {
        "year": year,
        "month": month,
        "total_cents": total,
        "recent_expenses": [
            {"id": str(item.id), "description": item.description, "amount_cents": item.amount_cents,
             "expense_date": item.expense_date.isoformat(), "subcategory": item.subcategory.name,
             "category": item.subcategory.category.name, "category_color": item.subcategory.category.color,
             "establishment": item.establishment.name}
            for item in recent
        ],
    }
