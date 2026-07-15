from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from uuid import UUID


class StageCreate(BaseModel):
    type: str
    outcome: Optional[str] = None
    notes: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class StageUpdate(BaseModel):
    type: Optional[str] = None
    outcome: Optional[str] = None
    notes: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class StageResponse(BaseModel):
    id: UUID
    application_id: UUID
    type: str
    outcome: Optional[str]
    notes: Optional[str]
    scheduled_at: Optional[datetime]
    completed_at: Optional[datetime]
    
    model_config = {"from_attributes": True}
    