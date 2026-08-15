from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ClientBase(BaseModel):
    first_name: str = Field(..., max_length=100)
    last_name: str = Field(..., max_length=100)
    email: Optional[EmailStr] = None
    birth_date: Optional[date] = None
    nationality: Optional[str] = Field(None, max_length=50)
    risk_score: float = Field(default=0.0, ge=0.0, le=100.0)
    is_pep: bool = False
    is_sanctioned: bool = False


class ClientCreate(ClientBase):
    pass


class ClientUpdate(BaseModel):
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None
    birth_date: Optional[date] = None
    nationality: Optional[str] = Field(None, max_length=50)
    risk_score: Optional[float] = Field(None, ge=0.0, le=100.0)
    is_pep: Optional[bool] = None
    is_sanctioned: Optional[bool] = None


class ClientRead(ClientBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
