from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from python_app.models.user import UserRole

class UserBase(BaseModel):
    email: EmailStr = Field(..., description="계정 이메일")

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100, description="비밀번호 8자 이상")

class UserLogin(UserBase):
    password: str = Field(..., description="비밀번호")

class UserResponse(UserBase):
    id: int
    role: UserRole
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)