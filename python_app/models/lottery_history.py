import enum
from datetime import datetime
from sqlalchemy import String, Enum, ForeignKey, Text, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from python_app.db.session import Base

class LotteryHistoryStatus(str, enum.Enum):
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    PENDING = "PENDING"

class LotteryHistory(Base):
    __tablename__ = "lottery_histories"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id", ondelete="CASCADE"), index=True)
    executor_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    draw_salt: Mapped[str] = mapped_column(String(64), nullable=False)
    total_applicants: Mapped[int] = mapped_column(nullable=False)
    winner_ids: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[LotteryHistoryStatus] = mapped_column(Enum(LotteryHistoryStatus), default=LotteryHistoryStatus.SUCCESS)
    executed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())