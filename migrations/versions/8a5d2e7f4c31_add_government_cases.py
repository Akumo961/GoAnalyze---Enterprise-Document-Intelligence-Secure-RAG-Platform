"""add durable government workflow cases

Revision ID: 8a5d2e7f4c31
Revises: 7c4f1b8e9a21
"""
from collections.abc import Sequence
import sqlalchemy as sa
from alembic import op

revision: str = "8a5d2e7f4c31"
down_revision: str | Sequence[str] | None = "7c4f1b8e9a21"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "government_cases",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.String(length=255), nullable=False),
        sa.Column("external_reference", sa.String(length=255), nullable=False),
        sa.Column("title", sa.String(length=1024), nullable=False),
        sa.Column("state", sa.String(length=32), nullable=False, server_default="intake"),
        sa.Column("priority", sa.String(length=32), nullable=False, server_default="normal"),
        sa.Column("assigned_queue", sa.String(length=255), nullable=True),
        sa.Column("assigned_to", sa.String(length=255), nullable=True),
        sa.Column("decision_officer", sa.String(length=255), nullable=True),
        sa.Column("decision_reason", sa.String(length=8192), nullable=True),
        sa.Column("attributes", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_government_cases_tenant_state", "government_cases", ["tenant_id", "state"])
    op.create_index("ix_government_cases_tenant_created", "government_cases", ["tenant_id", "created_at"])


def downgrade() -> None:
    op.drop_index("ix_government_cases_tenant_created", table_name="government_cases")
    op.drop_index("ix_government_cases_tenant_state", table_name="government_cases")
    op.drop_table("government_cases")
