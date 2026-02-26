from datetime import datetime
from pydantic import BaseModel, ConfigDict

class NotificationResponse(BaseModel):
    id: int
    title: str
    content: str
    is_read: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)