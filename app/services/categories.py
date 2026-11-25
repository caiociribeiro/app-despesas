from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from fastapi import HTTPException

from app.models import Category, Subcategory, Expense


def list_categories(db: Session) -> list[Category]:
    return list(db.scalars(select(Category).options(selectinload(Category.subcategories)).order_by(Category.name)))


def create_category(db: Session, name: str, color: str, initial_subcategory: str) -> Category:
    category = Category(name=name.strip(), color=color.upper())
    category.subcategories.append(Subcategory(name=initial_subcategory.strip()))
    db.add(category)
    db.commit()
    db.refresh(category)
    return db.scalar(select(Category).options(selectinload(Category.subcategories)).where(Category.id == category.id))


def add_subcategory(db: Session, category_id: UUID, name: str) -> Subcategory:
    category = db.get(Category, category_id)
    if not category:
        raise HTTPException(404, "Categoria não encontrada.")
    subcategory = Subcategory(category_id=category_id, name=name.strip())
    db.add(subcategory)
    db.commit()
    db.refresh(subcategory)
    return subcategory


def delete_subcategory(db: Session, subcategory_id: UUID) -> None:
    subcategory = db.get(Subcategory, subcategory_id)
    if not subcategory:
        raise HTTPException(404, "Subcategoria não encontrada.")
    count = db.query(Subcategory).filter(Subcategory.category_id == subcategory.category_id).count()
    if count <= 1:
        raise HTTPException(409, "A categoria precisa manter pelo menos uma subcategoria.")
    if db.query(Expense).filter(Expense.subcategory_id == subcategory_id).first():
        raise HTTPException(409, "A subcategoria possui despesas vinculadas.")
    db.delete(subcategory)
    db.commit()
