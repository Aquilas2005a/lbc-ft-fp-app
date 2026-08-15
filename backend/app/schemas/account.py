import re
from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

ACCOUNT_NUMBER_PATTERN = re.compile(r"^[A-Z]{2}[A-Z0-9]{13,32}$")



class AccountBase(BaseModel):
    account_number: str = Field(..., max_length=50)
    balance: Decimal = Field(default=Decimal("0.00"), ge=0, max_digits=18, decimal_places=2)
    currency: str = Field(default="EUR", max_length=10)
    status: str = Field(default="active", max_length=20)

    @field_validator("account_number")
    @classmethod
    def normalize_account_number(cls, value: str) -> str:
        normalized = value.replace(" ", "").upper()
        if not ACCOUNT_NUMBER_PATTERN.fullmatch(normalized):
            raise ValueError("Le numero de compte doit respecter un format IBAN simple.")
        return normalized

    @field_validator("currency")
    @classmethod
    def normalize_currency(cls, value: str) -> str:
        normalized = value.strip().upper()
        if len(normalized) != 3:
            raise ValueError("La devise doit etre un code ISO a trois lettres.")
        return normalized


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
