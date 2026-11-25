from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class SubcategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=80)


class SubcategoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str


class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    color: str = Field(default="#64748B", pattern=r"^#[0-9A-Fa-f]{6}$")
    initial_subcategory: str = Field(min_length=1, max_length=80)


class CategoryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=80)
    color: str | None = Field(default=None, pattern=r"^#[0-9A-Fa-f]{6}$")


class CategoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
    color: str
    subcategories: list[SubcategoryRead]
