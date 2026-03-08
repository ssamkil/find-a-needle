from datetime import datetime, timezone
from pytz import timezone
from sqlalchemy import select
from python_app.db.session import AsyncSessionLocal
from python_app.models import Event, EventStatus
from python_app.services.auto_draw import perform_draw


async def draw_task():
    async with AsyncSessionLocal() as db:
        now = datetime.now(timezone('Asia/Seoul'))

        stmt = select(Event).where(
            Event.status == EventStatus.OPEN,
            Event.end_at <= now
        )

        try:
            result = await db.execute(stmt)
            expired_events = result.scalars().all()

            if not expired_events:
                return

            for event in expired_events:
                try:
                    print(f"[자동 추첨] 이벤트 ID {event.id} ('{event.title}') 처리 시작...")

                    await perform_draw(
                        event_id=event.id,
                        db=db,
                        executor_id=1
                    )

                    await db.commit()
                    print(f"[자동 추첨] 이벤트 {event.id} 완료!")

                except Exception as e:
                    await db.rollback()
                    print(f"[자동 추첨] 이벤트 {event.id} 에러 발생: {str(e)}")
                    continue

        except Exception as e:
            print(f"[자동 추첨] 쿼리 실행 중 전체 오류 발생: {str(e)}")