"""add transaction counterparty country

Revision ID: 0006_tx_counterparty_country
Revises: 0005_add_audit_log_indexes
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0006_tx_counterparty_country"
down_revision: Union[str, None] = "0005_add_audit_log_indexes"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("transactions", sa.Column("counterparty_country", sa.String(length=2), nullable=True))
    op.create_index("ix_transactions_counterparty_country", "transactions", ["counterparty_country"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_transactions_counterparty_country", table_name="transactions")
    op.drop_column("transactions", "counterparty_country")
