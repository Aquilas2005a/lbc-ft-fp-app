from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class TransactionBase(BaseModel):
    amount: Decimal = Field(..., gt=0, max_digits=18, decimal_places=2)
    currency: str = Field(default="EUR", max_length=10)
    transaction_type: str = Field(default="transfer", max_length=30)
    status: str = Field(default="completed", max_length=20)
    counterparty_name: Optional[str] = Field(None, max_length=150)
    counterparty_account: Optional[str] = Field(None, max_length=50)


class TransactionCreate(TransactionBase):
    account_id: int


class TransactionRead(TransactionBase):
    id: int
    account_id: int
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)
