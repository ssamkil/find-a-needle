from datetime import datetime
from pydantic import BaseModel, ConfigDict

class WinnerResponse(BaseModel):
    id: int
    user_id: int
    event_id: int
    won_at: datetime

    model_config = ConfigDict(from_attributes=True)