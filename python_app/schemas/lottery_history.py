import json
from datetime import datetime
from typing import List
from pydantic import BaseModel, Field, ConfigDict
from python_app.models.lottery_history import LotteryHistoryStatus

class LotteryHistoryResponse(BaseModel):
    id: int
    event_id: int
    executor_id: int
    draw_salt: str = Field(..., max_length=64)
    total_applicants: int
    winner_ids: List[int]
    status: LotteryHistoryStatus
    executed_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def model_validate(cls, obj, **kwargs):
        if hasattr(obj, 'winner_ids') and isinstance(obj.winner_ids, str):
            try:
                obj.winner_ids = json.loads(obj.winner_ids)
            except json.JSONDecodeError:
                obj.winner_ids = []
        return super().model_validate(obj, **kwargs)