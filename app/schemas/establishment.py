from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class EstablishmentCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)


class EstablishmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
