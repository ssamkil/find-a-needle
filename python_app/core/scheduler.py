from apscheduler.schedulers.asyncio import AsyncIOScheduler
from python_app.tasks import draw_task

scheduler = AsyncIOScheduler()


def start_scheduler():
    scheduler.add_job(
        draw_task,
        "interval",
        minutes=1,
        id="auto_raffle_draw",
        replace_existing=True
    )

    scheduler.start()

def stop_scheduler():
    scheduler.shutdown()