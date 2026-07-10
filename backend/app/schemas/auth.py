from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr

# User
class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    created_at: datetime

    model_config = {"from_attributes": True}

# Auth
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    email: Optional[str] = None