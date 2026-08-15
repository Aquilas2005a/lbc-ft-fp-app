from datetime import datetime
from decimal import Decimal
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


TransactionType = Literal["credit", "debit", "deposit", "transfer", "withdrawal"]
TransactionStatus = Literal["completed", "flagged", "pending", "rejected"]


class TransactionBase(BaseModel):
    amount: Decimal = Field(..., gt=0, max_digits=18, decimal_places=2)
    currency: str = Field(default="EUR", max_length=10)
    transaction_type: TransactionType = "transfer"
    status: TransactionStatus = "completed"
    counterparty_name: Optional[str] = Field(None, max_length=150)
    counterparty_account: Optional[str] = Field(None, max_length=50)
    counterparty_country: Optional[str] = Field(None, min_length=2, max_length=2)

    @field_validator("currency")
    @classmethod
    def normalize_currency(cls, value: str) -> str:
        normalized = value.strip().upper()
        if len(normalized) != 3:
            raise ValueError("La devise doit etre un code ISO a trois lettres.")
        return normalized

    @field_validator("counterparty_country")
    @classmethod
    def normalize_counterparty_country(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        normalized = value.strip().upper()
        if len(normalized) != 2 or not normalized.isalpha():
            raise ValueError("Le pays de contrepartie doit etre un code ISO alpha-2.")
        return normalized


class TransactionCreate(TransactionBase):
    account_id: int


class TransactionRead(TransactionBase):
    id: int
    account_id: int
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)
