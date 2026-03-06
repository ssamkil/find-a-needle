from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from python_app.models.event import EventStatus

class EventBase(BaseModel):
    title: str = Field(..., min_length=2, max_length=300)
    description: Optional[str] = Field(None, max_length=1500)
    max_applicants: int = Field(default=10000, gt=0, lt=10001)
    start_at: datetime
    end_at: datetime

class EventCreate(EventBase):
    pass

class EventResponse(EventBase):
    id: int
    creator_id: int
    status: EventStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)