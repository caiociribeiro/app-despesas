"""Create initial expense management schema.

Revision ID: 0001_initial
Revises:
Create Date: 2026-11-25
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "categories",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(length=80), nullable=False),
        sa.Column("color", sa.String(length=7), nullable=False, server_default="#64748B"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("length(trim(name)) > 0", name="ck_categories_name_not_empty"),
        sa.CheckConstraint("color ~ '^#[0-9A-Fa-f]{6}$'", name="ck_categories_color_hex"),
        sa.UniqueConstraint("name", name="uq_categories_name"),
    )
    op.create_table(
        "payment_methods",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(length=40), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("name", name="uq_payment_methods_name"),
    )
    op.create_table(
        "subcategories",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("category_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("categories.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(length=80), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("length(trim(name)) > 0", name="ck_subcategories_name_not_empty"),
        sa.UniqueConstraint("category_id", "name", name="uq_subcategories_category_name"),
    )
    op.create_index("ix_subcategories_category_id", "subcategories", ["category_id"])
    op.create_table(
        "expenses",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("description", sa.String(length=160), nullable=False),
        sa.Column("amount_cents", sa.Integer(), nullable=False),
        sa.Column("expense_date", sa.Date(), nullable=False),
        sa.Column("subcategory_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("subcategories.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("payment_method_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("payment_methods.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("amount_cents > 0", name="ck_expenses_amount_positive"),
        sa.CheckConstraint("length(trim(description)) > 0", name="ck_expenses_description_not_empty"),
    )
    op.create_index("ix_expenses_expense_date", "expenses", ["expense_date"])
    op.create_index("ix_expenses_subcategory_date", "expenses", ["subcategory_id", "expense_date"])

    payment_methods = sa.table("payment_methods", sa.column("id", postgresql.UUID(as_uuid=True)), sa.column("name", sa.String), sa.column("is_active", sa.Boolean))
    import uuid
    op.bulk_insert(payment_methods, [
        {"id": uuid.uuid4(), "name": name, "is_active": True}
        for name in ("PIX", "Boleto", "Cartão de crédito", "Cartão de débito", "Dinheiro / Outro")
    ])


def downgrade() -> None:
    op.drop_index("ix_expenses_subcategory_date", table_name="expenses")
    op.drop_index("ix_expenses_expense_date", table_name="expenses")
    op.drop_table("expenses")
    op.drop_index("ix_subcategories_category_id", table_name="subcategories")
    op.drop_table("subcategories")
    op.drop_table("payment_methods")
    op.drop_table("categories")
