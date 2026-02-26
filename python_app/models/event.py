import enum
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Enum, DateTime, Text, func
from sqlalchemy.orm import Mapped, mapped_column
from python_app.db.session import Base

class EventStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    COMPLETED = "COMPLETED"

class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(1500), nullable=True)
    max_applicants: Mapped[int] = mapped_column(default=10000)
    start_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[EventStatus] = mapped_column(Enum(EventStatus), default=EventStatus.DRAFT)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())