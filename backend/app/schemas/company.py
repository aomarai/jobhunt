from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class CompanyCreate(BaseModel):
    name: str
    website: Optional[str] = None
    notes: Optional[str] = None


class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    website: Optional[str] = None
    notes: Optional[str] = None


class CompanyResponse(BaseModel):
    id: UUID
    name: str
    website: Optional[str]
    notes: Optional[str]
    
    model_config = {"from_attributes": True}

    