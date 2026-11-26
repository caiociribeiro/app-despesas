from datetime import date
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ExpenseCreate(BaseModel):
    description: str = Field(min_length=1, max_length=160)
    amount_cents: int = Field(gt=0)
    expense_date: date
    subcategory_id: UUID
    establishment_id: UUID
    payment_method_id: UUID
    tag_names: list[str] = Field(default_factory=list, max_length=10)
    notes: str | None = None


class ExpenseUpdate(BaseModel):
    description: str | None = Field(default=None, min_length=1, max_length=160)
    amount_cents: int | None = Field(default=None, gt=0)
    expense_date: date | None = None
    subcategory_id: UUID | None = None
    establishment_id: UUID | None = None
    payment_method_id: UUID | None = None
    tag_names: list[str] | None = Field(default=None, max_length=10)
    notes: str | None = None


class TagSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str


class ExpenseRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    description: str
    amount_cents: int
    expense_date: date
    subcategory_id: UUID
    establishment_id: UUID
    payment_method_id: UUID
    notes: str | None
    tags: list[TagSummary] = Field(default_factory=list)
