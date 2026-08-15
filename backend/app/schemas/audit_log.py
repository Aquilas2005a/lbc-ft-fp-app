from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class AuditLogBase(BaseModel):
    action: str = Field(..., max_length=100)
    entity_type: str = Field(..., max_length=50)
    entity_id: Optional[str] = Field(None, max_length=50)
    details: Optional[str] = None


class AuditLogCreate(AuditLogBase):
    user_id: Optional[str] = Field(None, max_length=100)


class AuditLogRead(AuditLogBase):
    id: int
    user_id: Optional[str] = None
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)
