from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from python_app.models.event import EventStatus

class EventBase(BaseModel):
    title: str = Field(..., min_length=2, max_length=150, description="이벤트 제목")
    description: Optional[str] = Field(None, max_length=1500, description="이벤트 상세 설명")
    max_applicants: int = Field(10000, ge=1, le=50000, description="최대 응모 가능 인원")
    start_at: datetime = Field(..., description="이벤트 시작 시간")
    end_at: datetime = Field(..., description="이벤트 종료 시간")

class EventCreate(EventBase):
    pass

class EventResponse(EventBase):
    id: int
    status: EventStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)