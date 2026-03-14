import pytz
from datetime import datetime
from sqlalchemy import select
from python_app.db.session import AsyncSessionLocal
from python_app.models import Event, EventStatus
from python_app.services.auto_draw import perform_draw

async def draw_task():
    async with AsyncSessionLocal() as db:
        now = datetime.now(pytz.timezone('Asia/Seoul'))

        query = select(Event).where(
            Event.status == EventStatus.OPEN,
            Event.end_at <= now
        )

        try:
            result = await db.execute(query)
            expired_events = result.scalars().all()

            if not expired_events:
                return

            for event in expired_events:
                try:
                    await perform_draw(
                        event_id=event.id,
                        db=db,
                        executor_id=event.creator_id
                    )

                    await db.commit()

                except Exception as e:
                    await db.rollback()
                    print(str(e))
                    continue

        except Exception as e:
            print(str(e))