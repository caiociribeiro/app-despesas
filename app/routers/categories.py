from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models import Category
from app.schemas.category import CategoryCreate, CategoryRead, CategoryUpdate, SubcategoryCreate, SubcategoryRead
from app.services.categories import add_subcategory, create_category, delete_subcategory, list_categories

router = APIRouter(prefix="/api/categories", tags=["categories"])


@router.get("", response_model=list[CategoryRead])
def get_categories(db: Session = Depends(get_db)):
    return list_categories(db)


@router.post("", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
def post_category(payload: CategoryCreate, db: Session = Depends(get_db)):
    try:
        return create_category(db, payload.name, payload.color, payload.initial_subcategory)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(409, "Já existe uma categoria com esse nome.") from exc


@router.patch("/{category_id}", response_model=CategoryRead)
def patch_category(category_id: UUID, payload: CategoryUpdate, db: Session = Depends(get_db)):
    category = db.get(Category, category_id)
    if not category:
        raise HTTPException(404, "Categoria não encontrada.")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(category, field, value.strip() if field == "name" and value else value.upper() if field == "color" and value else value)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(409, "Já existe uma categoria com esse nome.") from exc
    return next(item for item in list_categories(db) if item.id == category_id)


@router.post("/{category_id}/subcategories", response_model=SubcategoryRead, status_code=201)
def post_subcategory(category_id: UUID, payload: SubcategoryCreate, db: Session = Depends(get_db)):
    try:
        return add_subcategory(db, category_id, payload.name)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(409, "Essa subcategoria já existe nessa categoria.") from exc


@router.delete("/subcategories/{subcategory_id}", status_code=204)
def remove_subcategory(subcategory_id: UUID, db: Session = Depends(get_db)):
    delete_subcategory(db, subcategory_id)
