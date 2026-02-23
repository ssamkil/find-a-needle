import os, asyncio, sentry_sdk, redis
from contextlib import asynccontextmanager
from datetime import datetime
from typing import List

from fastapi import FastAPI, HTTPException, status
from sentry_sdk.integrations.fastapi import FastApiIntegration
from apscheduler.schedulers.background import BackgroundScheduler

from database import engine, Base, AsyncSessionLocal, Winner
from sqlalchemy import select

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    integrations=[FastApiIntegration()],
    traces_sample_rate=1.0,
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("DB 테이블 생성 완료")

    yield

    print("서버 종료")

app = FastAPI(title="Find-a-Needle Worker & API", lifespan=lifespan)
rd = redis.from_url(os.getenv("REDIS_URL", "redis://redis:6379"), decode_responses=True)

async def move_redis_to_db():
    print(f"[{datetime.now()}] 배치 시작")
    winners_list: List[str] = list(rd.smembers("applied_users"))

    if not winners_list:
        return

    async with AsyncSessionLocal() as session:
        try:
            async with session.begin():
                for uid in winners_list:
                    new_winner = Winner(user_id=uid)
                    session.add(new_winner)
            await session.commit()
            print(f"성공: {len(winners_list)}명의 당첨자를 DB로 이전했습니다.")
        except Exception as e:
            print(f"에러 발생: {e}")
            await session.rollback()


def scheduled_task():
    asyncio.run(move_redis_to_db())

scheduler = BackgroundScheduler()
scheduler.add_job(scheduled_task, 'interval', minutes=1)
scheduler.start()

# 최신 lifespan 으로 변경
# @app.on_event("startup")
# async def startup():
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)

@app.get("/api/check/{user_id}")
async def check_winner(user_id: str):
    async with AsyncSessionLocal() as session:
        query = select(Winner).where(Winner.user_id == user_id)
        result = await session.execute(query)
        winner = result.scalar_one_or_none()

        if not winner:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{user_id}님은 당첨자 명단에 없습니다."
            )

        return {
            "status": "SUCCESS",
            "user_id": winner.user_id,
            "won_at": winner.won_at,
            "message": "축하합니다! 이벤트 당첨자로 확인되었습니다."
        }

@app.get("/api/debug-sentry")
def trigger_error():
    raise ValueError("Sentry Test Error")