from typing import List, Optional
from pydantic import BaseModel, Field, computed_field, ConfigDict

class WinnerResponse(BaseModel):
    id: int
    user_id: int
    event_id: int

    model_config = ConfigDict(from_attributes=True)

class WinnerInfo(BaseModel):
    user_id: int
    nickname: str
    email: str

    @computed_field
    @property
    def masked_email(self) -> str:
        try:
            local, domain = self.email.split("@")
            if len(local) <= 3:
                return local[0] + "*" * (len(local) - 1) + "@" + domain
            return local[:3] + "*" * (len(local) - 3) + "@" + domain
        except (ValueError, AttributeError):
            return "******@****.***"

class LotteryStats(BaseModel):
    total_applicants: int = Field(..., description="총 응모자 수")
    winner_count: int = Field(..., description="당첨 인원")
    competition_rate: str = Field(..., description="경쟁률")

class LotteryResultResponse(BaseModel):
    event_id: int
    event_title: str
    statistics: LotteryStats
    winners: List[WinnerInfo]

    model_config = ConfigDict(from_attributes=True)

class AdminWinnerInfo(BaseModel):
    user_id: int
    name: str
    email: str

class AdminLotteryResultResponse(BaseModel):
    event_id: int
    event_title: str
    statistics: LotteryStats
    winners: List[AdminWinnerInfo]

    model_config = ConfigDict(from_attributes=True)