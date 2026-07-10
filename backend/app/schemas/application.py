from uuid import UUID
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class ApplicationCreate(BaseModel):
    company_id: UUID
    job_id: Optional[str] = None
    job_title: str
    job_url: Optional[str] = None
    status: str = "applied"
    notes: Optional[str] = None


class ApplicationUpdate(BaseModel):
    job_title: Optional[str] = None
    job_url: Optional[str] = None
    status:  Optional[str] = None
    notes: Optional[str] = None


class ApplicationResponse(BaseModel):
    id: UUID
    user_id: UUID
    job_id: Optional[str]
    job_title: str
    job_url: Optional[str]
    notes: Optional[str]
    applied_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}