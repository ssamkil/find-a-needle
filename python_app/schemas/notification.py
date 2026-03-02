from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class NotificationBase(BaseModel):
    title: str = Field(..., max_length=300)
    content: str = Field(..., max_length=1500)

class NotificationResponse(NotificationBase):
    id: int
    user_id: int
    is_read: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)