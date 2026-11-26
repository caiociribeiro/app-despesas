from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, Index, Integer, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.connection import Base


class Expense(Base):
    __tablename__ = "expenses"
    __table_args__ = (
        CheckConstraint("amount_cents > 0", name="ck_expenses_amount_positive"),
        CheckConstraint("length(trim(description)) > 0", name="ck_expenses_description_not_empty"),
        Index("ix_expenses_expense_date", "expense_date"),
        Index("ix_expenses_subcategory_date", "subcategory_id", "expense_date"),
        Index("ix_expenses_establishment_id", "establishment_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    description: Mapped[str] = mapped_column(String(160), nullable=False)
    amount_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    expense_date: Mapped[date] = mapped_column(Date, nullable=False)
    subcategory_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("subcategories.id", ondelete="RESTRICT"), nullable=False)
    establishment_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("establishments.id", ondelete="RESTRICT"), nullable=False)
    payment_method_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("payment_methods.id", ondelete="RESTRICT"), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    subcategory = relationship("Subcategory")
    payment_method = relationship("PaymentMethod")
    establishment = relationship("Establishment")
    tags = relationship("Tag", secondary="expense_tags", back_populates="expenses", order_by="Tag.name")
