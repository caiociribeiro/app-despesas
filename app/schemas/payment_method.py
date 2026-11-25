from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class PaymentMethodCreate(BaseModel):
    name: str = Field(min_length=1, max_length=40)


class PaymentMethodRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
    is_active: bool
