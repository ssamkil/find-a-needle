from datetime import datetime
from pydantic import BaseModel, ConfigDict

class LotteryHistoryResponse(BaseModel):
    id: int
    event_id: int
    draw_salt: str = "추첨 시 사용된 고유 솔트값"
    total_applicants: int
    winner_count: int
    executed_at: datetime

    model_config = ConfigDict(from_attributes=True)