from datetime import datetime, timezone
from decimal import Decimal
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.account import Account
    from app.models.alert import Alert


class Transaction(Base):
    __tablename__ = "transactions"
    __table_args__ = (
        CheckConstraint("amount > 0", name="ck_transactions_amount_positive"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="EUR", nullable=False)
    transaction_type: Mapped[str] = mapped_column(String(30), default="transfer", nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="completed", nullable=False)
    counterparty_name: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    counterparty_account: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    counterparty_country: Mapped[Optional[str]] = mapped_column(String(2), nullable=True, index=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    account: Mapped["Account"] = relationship("Account", back_populates="transactions")
    alerts: Mapped[List["Alert"]] = relationship("Alert", back_populates="transaction")
