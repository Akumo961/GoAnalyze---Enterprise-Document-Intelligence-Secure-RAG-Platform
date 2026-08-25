"""add persistent regulatory knowledge tables

Revision ID: 7c4f1b8e9a21
Revises: ed3a4f8a50b6
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "7c4f1b8e9a21"
down_revision: str | Sequence[str] | None = "ed3a4f8a50b6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "regulatory_sources",
        sa.Column("source_id", sa.String(length=255), nullable=False),
        sa.Column("title", sa.String(length=1024), nullable=False),
        sa.Column("knowledge_type", sa.String(length=64), nullable=False),
        sa.Column("jurisdiction", sa.String(length=255), nullable=False),
        sa.Column("publisher", sa.String(length=512), nullable=False),
        sa.Column("authority", sa.String(length=64), nullable=False),
        sa.Column("authoritative", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("source_uri", sa.String(length=2048), nullable=False),
        sa.Column("effective_from", sa.Date(), nullable=True),
        sa.Column("effective_to", sa.Date(), nullable=True),
        sa.Column("version", sa.String(length=64), nullable=False),
        sa.PrimaryKeyConstraint("source_id"),
    )
    op.create_index("ix_regulatory_sources_jurisdiction", "regulatory_sources", ["jurisdiction"])
    op.create_index("ix_regulatory_sources_source_id_version", "regulatory_sources", ["source_id", "version"], unique=True)

    op.create_table(
        "regulatory_obligations",
        sa.Column("obligation_id", sa.String(length=255), nullable=False),
        sa.Column("source_id", sa.String(length=255), nullable=False),
        sa.Column("title", sa.String(length=1024), nullable=False),
        sa.Column("description", sa.String(length=8192), nullable=False),
        sa.Column("evidence_requirements", sa.JSON(), nullable=False),
        sa.Column("jurisdiction", sa.String(length=255), nullable=False),
        sa.Column("effective_from", sa.Date(), nullable=True),
        sa.Column("effective_to", sa.Date(), nullable=True),
        sa.Column("exceptions", sa.JSON(), nullable=False),
        sa.Column("verified", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.PrimaryKeyConstraint("obligation_id"),
    )
    op.create_index("ix_regulatory_obligations_source_id", "regulatory_obligations", ["source_id"])
    op.create_index("ix_regulatory_obligations_jurisdiction", "regulatory_obligations", ["jurisdiction"])


def downgrade() -> None:
    op.drop_index("ix_regulatory_obligations_jurisdiction", table_name="regulatory_obligations")
    op.drop_index("ix_regulatory_obligations_source_id", table_name="regulatory_obligations")
    op.drop_table("regulatory_obligations")
    op.drop_index("ix_regulatory_sources_source_id_version", table_name="regulatory_sources")
    op.drop_index("ix_regulatory_sources_jurisdiction", table_name="regulatory_sources")
    op.drop_table("regulatory_sources")
