from pydantic import BaseModel, EmailStr, ConfigDict, Field
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    USER = "USER"
    ADMIN = "ADMIN"

class UserBase(BaseModel):
    email: EmailStr = Field(..., max_length=300)
    nickname: str = Field(..., min_length=2, max_length=10)

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, description="비밀번호는 최소 8자 이상이어야 합니다.")

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: int
    role: UserRole
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)