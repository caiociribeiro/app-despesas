from __future__ import annotations

import uuid

from sqlalchemy import CheckConstraint, Column, ForeignKey, String, Table, Uuid, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.connection import Base


expense_tags = Table(
    "expense_tags",
    Base.metadata,
    Column("expense_id", Uuid(as_uuid=True), ForeignKey("expenses.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", Uuid(as_uuid=True), ForeignKey("tags.id", ondelete="RESTRICT"), primary_key=True),
)


class Tag(Base):
    __tablename__ = "tags"
    __table_args__ = (
        UniqueConstraint("normalized_name", name="uq_tags_normalized_name"),
        CheckConstraint("length(trim(name)) > 0", name="ck_tags_name_not_empty"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    normalized_name: Mapped[str] = mapped_column(String(50), nullable=False)
    expenses: Mapped[list["Expense"]] = relationship(secondary=expense_tags, back_populates="tags")
