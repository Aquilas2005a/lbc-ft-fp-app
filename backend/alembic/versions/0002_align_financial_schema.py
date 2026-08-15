"""align financial schema with ORM models

Revision ID: 0002_align_financial_schema
Revises: 0001_initial_tables
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0002_align_financial_schema"
down_revision: Union[str, None] = "0001_initial_tables"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "accounts",
        "balance",
        existing_type=sa.Float(),
        type_=sa.Numeric(precision=18, scale=2),
        existing_nullable=False,
        postgresql_using="balance::numeric(18,2)",
    )
    op.create_check_constraint(
        "ck_accounts_balance_nonnegative",
        "accounts",
        "balance >= 0",
    )
    op.alter_column(
        "transactions",
        "amount",
        existing_type=sa.Float(),
        type_=sa.Numeric(precision=18, scale=2),
        existing_nullable=False,
        postgresql_using="amount::numeric(18,2)",
    )
    op.create_check_constraint(
        "ck_transactions_amount_positive",
        "transactions",
        "amount > 0",
    )


def downgrade() -> None:
    op.drop_constraint("ck_transactions_amount_positive", "transactions")
    op.alter_column(
        "transactions",
        "amount",
        existing_type=sa.Numeric(precision=18, scale=2),
        type_=sa.Float(),
        existing_nullable=False,
        postgresql_using="amount::double precision",
    )
    op.drop_constraint("ck_accounts_balance_nonnegative", "accounts")
    op.alter_column(
        "accounts",
        "balance",
        existing_type=sa.Numeric(precision=18, scale=2),
        type_=sa.Float(),
        existing_nullable=False,
        postgresql_using="balance::double precision",
    )
