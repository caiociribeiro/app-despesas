"""Add reusable tags and expense-tag association.

Revision ID: 0003_add_tags
Revises: 0002_add_establishments
"""

from alembic import op
import sqlalchemy as sa

revision = "0003_add_tags"
down_revision = "0002_establishments"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "tags",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("normalized_name", sa.String(length=50), nullable=False),
        sa.CheckConstraint("length(trim(name)) > 0", name="ck_tags_name_not_empty"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("normalized_name", name="uq_tags_normalized_name"),
    )
    op.create_table(
        "expense_tags",
        sa.Column("expense_id", sa.Uuid(), nullable=False),
        sa.Column("tag_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(["expense_id"], ["expenses.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tag_id"], ["tags.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("expense_id", "tag_id"),
    )


def downgrade() -> None:
    op.drop_table("expense_tags")
    op.drop_table("tags")
