from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


AlertSeverity = Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
AlertStatus = Literal["OPEN", "VALIDATED", "REJECTED", "ESCALATED"]


class AlertBase(BaseModel):
    alert_type: str = Field(..., max_length=50)
    severity: AlertSeverity = "MEDIUM"
    status: AlertStatus = "OPEN"
    description: str


class AlertCreate(AlertBase):
    client_id: Optional[int] = None
    transaction_id: Optional[int] = None


class AlertUpdate(BaseModel):
    status: AlertStatus
    review_note: str = Field(..., min_length=3, max_length=2000)


class AlertRead(AlertBase):
    id: int
    client_id: Optional[int] = None
    transaction_id: Optional[int] = None
    review_note: Optional[str] = None
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
