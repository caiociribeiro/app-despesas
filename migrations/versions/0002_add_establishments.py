"""Add required establishment to expenses.

Revision ID: 0002_establishments
Revises: 0001_initial
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid

revision = "0002_establishments"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "establishments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("normalized_name", sa.String(length=120), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("normalized_name", name="uq_establishments_normalized_name"),
        sa.CheckConstraint("length(trim(name)) > 0", name="ck_establishments_name_not_empty"),
    )

    # Preserve any existing expenses while making the new field mandatory.
    fallback_id = uuid.uuid4()
    establishments = sa.table(
        "establishments",
        sa.column("id", postgresql.UUID(as_uuid=True)),
        sa.column("name", sa.String()),
        sa.column("normalized_name", sa.String()),
    )
    op.bulk_insert(establishments, [{
        "id": fallback_id,
        "name": "Não informado",
        "normalized_name": "não informado",
    }])

    op.add_column("expenses", sa.Column("establishment_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.execute(sa.text("UPDATE expenses SET establishment_id = :establishment_id").bindparams(establishment_id=fallback_id))
    op.alter_column("expenses", "establishment_id", nullable=False)
    op.create_foreign_key(
        "fk_expenses_establishment_id_establishments",
        "expenses",
        "establishments",
        ["establishment_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_index("ix_expenses_establishment_id", "expenses", ["establishment_id"])


def downgrade() -> None:
    op.drop_index("ix_expenses_establishment_id", table_name="expenses")
    op.drop_constraint("fk_expenses_establishment_id_establishments", "expenses", type_="foreignkey")
    op.drop_column("expenses", "establishment_id")
    op.drop_table("establishments")
