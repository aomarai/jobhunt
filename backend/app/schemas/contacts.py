from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class ContactCreate(BaseModel):
    name: str
    role: Optional[str] = None
    email: Optional[str] = None
    linkedin_url: Optional[str] = None
    notes: Optional[str] = None


class ContactUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    email: Optional[str] = None
    linkedin_url: Optional[str] = None
    notes: Optional[str] = None


class ContactResponse(BaseModel):
    id: UUID
    company_id: UUID
    application_id: UUID
    name: str
    role: Optional[str]
    email: Optional[str]
    linkedin_url: Optional[str]
    notes: Optional[str]

    model_config = {"from_attributes": True}