"""add_alert_review_fields

Revision ID: 0004_add_alert_review_fields
Revises: 0003_add_client_soft_delete
Create Date: 2026-08-15 08:00:00.000000

Ajoute les colonnes review_note, reviewed_by et reviewed_at sur la table alerts,
nécessaires pour le workflow de revue manuelle des alertes (T17).
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0004_add_alert_review_fields"
down_revision: Union[str, None] = "0003_add_client_soft_delete"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("alerts", sa.Column("review_note", sa.Text(), nullable=True))
    op.add_column("alerts", sa.Column("reviewed_by", sa.String(length=100), nullable=True))
    op.add_column(
        "alerts",
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("alerts", "reviewed_at")
    op.drop_column("alerts", "reviewed_by")
    op.drop_column("alerts", "review_note")
