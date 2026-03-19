import hashlib, json, pytz
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from python_app.models import Event, EventStatus, Winner, LotteryHistory, LotteryHistoryStatus
from python_app.core import settings, rd


async def perform_draw(event_id: int, db, executor_id: int):
    lock_key = f"lock:event:{event_id}:draw"

    is_locked = await rd.set(lock_key, "processing", nx=True, ex=60)

    if not is_locked:
        raise ValueError("해당 이벤트에 대한 추첨이 진행 중입니다.")

    try:
        result = await db.execute(
            select(Event).where(Event.id == event_id).with_for_update()
        )
        event = result.scalar_one_or_none()

        if not event or event.status != EventStatus.OPEN:
            raise ValueError("추첨 가능한 상태가 아닙니다.")

        redis_key = f"event:{event_id}:applicants"
        applicants = []

        async for member in rd.sscan_iter(redis_key, count=1000):
            applicants.append(member)

        if not applicants:
            raise ValueError("응모자가 없습니다.")

        def generate_hash(user_id: str):
            combined_str = f"{settings.SECRET_KEY}{event_id}{user_id}"
            return hashlib.sha256(combined_str.encode()).hexdigest()

        hashed_applicants = [(uid, generate_hash(uid)) for uid in applicants]
        hashed_applicants.sort(key=lambda x: x[1])

        draw_count = min(len(applicants), event.max_applicants)
        winner_ids = [item[0] for item in hashed_applicants[:draw_count]]

        if winner_ids:
            values = [{"event_id": event_id, "user_id": int(uid)} for uid in winner_ids]
            query = insert(Winner).values(values).on_conflict_do_nothing(
                index_elements=["event_id", "user_id"]
            )
            await db.execute(query)

        db.add(LotteryHistory(
            event_id=event_id,
            executor_id=executor_id,
            draw_salt=settings.SECRET_KEY[:8],
            executed_at=datetime.now(pytz.timezone('Asia/Seoul')),
            total_applicants=len(applicants),
            winner_ids=json.dumps(winner_ids),
            status=LotteryHistoryStatus.SUCCESS
        ))

        event.status = EventStatus.COMPLETED

        await rd.delete(redis_key)

        return {
            "message": "추첨이 완료되었습니다.",
            "total_applicants": len(applicants),
            "winners_count": len(winner_ids)
        }

    except Exception as e:
        raise e

    finally:
        await rd.delete(lock_key)