import pytz
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone
from python_app.db.session import get_db
from python_app.models import User, Event, EventStatus
from python_app.api import dependencies
from python_app.core import rd

router = APIRouter()


@router.post("/{event_id}")
async def apply_to_event(
        event_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(dependencies.get_current_user)
):
    result = await db.execute(select(Event).where(Event.id == event_id))
    event = result.scalar_one_or_none()

    if not event:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail="존재하지 않는 이벤트입니다."
        )

    if event.status != EventStatus.OPEN:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="현재 응모 가능한 상태가 아닙니다."
        )

    now = datetime.now(pytz.timezone('Asia/Seoul'))
    if now < event.start_at or now > event.end_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="응모 시간이 아닙니다."
        )

    redis_key = f"event:{event_id}:applicants"

    is_new_applicant = await rd.sadd(redis_key, current_user.id)

    if is_new_applicant == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 이 이벤트에 응모하셨습니다."
        )

    return {
        "message": "응모가 성공적으로 완료되었습니다.",
        "event_title": event.title,
        "user_email": current_user.email
    }