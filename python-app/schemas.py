from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime
    class Config:
        from_attributes = True

class EventCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=2000)
    max_applicants: int = Field(10000, ge=1, le=50000)
    start_at: datetime
    end_at: datetime

class EventResponse(EventCreate):
    id: int
    status: str
    class Config:
        from_attributes = True