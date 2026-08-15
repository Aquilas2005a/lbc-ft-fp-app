from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class AlertBase(BaseModel):
    alert_type: str = Field(..., max_length=50)
    severity: str = Field(default="MEDIUM", max_length=20)
    status: str = Field(default="OPEN", max_length=20)
    description: str


class AlertCreate(AlertBase):
    client_id: Optional[int] = None
    transaction_id: Optional[int] = None


class AlertUpdate(BaseModel):
    severity: Optional[str] = Field(None, max_length=20)
    status: Optional[str] = Field(None, max_length=20)
    description: Optional[str] = None


class AlertRead(AlertBase):
    id: int
    client_id: Optional[int] = None
    transaction_id: Optional[int] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
