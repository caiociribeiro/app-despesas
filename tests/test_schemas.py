import pytest
from pydantic import ValidationError

from app.schemas.category import CategoryCreate
from app.schemas.expense import ExpenseCreate


def test_category_requires_initial_subcategory():
    with pytest.raises(ValidationError):
        CategoryCreate(name="Alimentação", color="#16A34A")


def test_category_accepts_valid_color_and_subcategory():
    category = CategoryCreate(name="Alimentação", color="#16A34A", initial_subcategory="Supermercado")
    assert category.color == "#16A34A"
    assert category.initial_subcategory == "Supermercado"


def test_expense_rejects_zero_or_negative_amount():
    from uuid import uuid4
    with pytest.raises(ValidationError):
        ExpenseCreate(description="Café", amount_cents=0, expense_date="2026-11-25", subcategory_id=uuid4(), payment_method_id=uuid4(), establishment_id=uuid4())


def test_expense_requires_establishment():
    from uuid import uuid4
    with pytest.raises(ValidationError):
        ExpenseCreate(
            description="Compra",
            amount_cents=1000,
            expense_date="2026-11-25",
            subcategory_id=uuid4(),
            payment_method_id=uuid4(),
        )


def test_expense_accepts_establishment():
    from uuid import uuid4
    establishment_id = uuid4()
    expense = ExpenseCreate(
        description="Compra",
        amount_cents=1000,
        expense_date="2026-11-25",
        subcategory_id=uuid4(),
        payment_method_id=uuid4(),
        establishment_id=establishment_id,
    )
    assert expense.establishment_id == establishment_id
