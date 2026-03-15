import pytz
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from python_app.db.session import get_db
from python_app.models import User, Event, EventStatus
from python_app.schemas import EventCreate, EventResponse
from python_app.api import dependencies

router = APIRouter()

@router.post("/", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
async def create_event(
        *,
        db: AsyncSession = Depends(get_db),
        event_in: EventCreate,
        current_admin: User = Depends(dependencies.get_current_admin)
):
    now = datetime.now(pytz.timezone('Asia/Seoul'))

    if event_in.start_at < now:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="시작 시간은 현재 시간보다 이후여야 합니다."
        )

    if event_in.end_at < event_in.start_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="종료 시간은 시작 시간보다 이후여야 합니다."
        )

    new_event = Event(
        **event_in.model_dump(),
        status=EventStatus.DRAFT,
        creator_id=current_admin.id
    )

    db.add(new_event)
    try:
        await db.commit()
        await db.refresh(new_event)
    except Exception as e:
        await db.rollback()
        raise e

    return new_event

@router.get("/", response_model=List[EventResponse])
async def read_events(
        db: AsyncSession = Depends(get_db),
        skip: int = 0,
        limit: int = 100
):
    result = await db.execute(
        select(Event).offset(skip).limit(limit).order_by(Event.id.desc())
    )
    events = result.scalars().all()
    return events

@router.get("/{event_id}", response_model=EventResponse)
async def read_event(
        event_id: int,
        db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Event).where(Event.id == event_id))
    event = result.scalar_one_or_none()

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="존재하지 않는 이벤트입니다."
        )
    return event