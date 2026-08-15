from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class AccountBase(BaseModel):
    account_number: str = Field(..., max_length=50)
    balance: Decimal = Field(default=Decimal("0.00"), ge=0, max_digits=18, decimal_places=2)
    currency: str = Field(default="EUR", max_length=10)
    status: str = Field(default="active", max_length=20)


class AccountCreate(AccountBase):
    client_id: int


class AccountUpdate(BaseModel):
    balance: Optional[Decimal] = Field(None, ge=0, max_digits=18, decimal_places=2)
    currency: Optional[str] = Field(None, max_length=10)
    status: Optional[str] = Field(None, max_length=20)


class AccountRead(AccountBase):
    id: int
    client_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
