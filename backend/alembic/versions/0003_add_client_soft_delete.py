"""add logical deletion to clients

Revision ID: 0003_add_client_soft_delete
Revises: 0002_align_financial_schema
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0003_add_client_soft_delete"
down_revision: Union[str, None] = "0002_align_financial_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("clients", sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True))
    op.create_index("ix_clients_deleted_at", "clients", ["deleted_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_clients_deleted_at", table_name="clients")
    op.drop_column("clients", "deleted_at")
