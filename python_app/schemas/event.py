from typing import Optional
from datetime import datetime
from pytz import timezone
from pydantic import BaseModel, Field, ConfigDict, model_validator
from python_app.models.event import EventStatus

class EventBase(BaseModel):
    title: str = Field(..., min_length=2, max_length=300)
    description: Optional[str] = Field(None, max_length=1500)
    max_applicants: int = Field(default=10000, gt=0, lt=10001)
    start_at: datetime
    end_at: datetime

class EventCreate(EventBase):
    @model_validator(mode='after')
    def validate_event_times(self) -> 'EventCreate':
        KST = timezone('Asia/Seoul')

        now = datetime.now(KST)

        def process_time(dt: datetime):
            if dt.tzinfo is None:
                return KST.localize(dt)
            return dt.astimezone(KST)

        start = process_time(self.start_at)
        end = process_time(self.end_at)

        if start < now:
            raise ValueError("이벤트 시작 시간은 현재 시간보다 이후여야 합니다.")

        if end <= start:
            raise ValueError("이벤트 종료 시간은 시작 시간보다 이후여야 합니다.")

        return self

class EventResponse(EventBase):
    id: int
    creator_id: int
    status: EventStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)