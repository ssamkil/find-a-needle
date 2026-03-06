import asyncio, sentry_sdk
from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sentry_sdk.integrations.fastapi import FastApiIntegration
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from python_app.db.session import AsyncSessionLocal
from python_app.api import api_router
from python_app.core import settings, rd
from python_app.models import Winner

if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        integrations=[FastApiIntegration()],
        traces_sample_rate=1.0,
    )

async def move_redis_to_db_task():
    keys = await rd.keys("event:*:applicants")

    for key in keys:
        try:
            event_id = int(key.split(":")[1])

            processing_key = f"{key}:processing"
            if await rd.exists(key):
                await rd.rename(key, processing_key)
            else:
                continue

            applicants = list(await rd.smembers(processing_key))

            if not applicants:
                await rd.delete(processing_key)
                continue

            async with AsyncSessionLocal() as session:
                async with session.begin():
                    for uid in applicants:
                        new_winner = Winner(user_id=int(uid), event_id=event_id)
                        session.add(new_winner)

                await rd.delete(processing_key)

        except Exception as e:
            sentry_sdk.capture_exception(e)

            if await rd.exists(processing_key):
                stuck_applicants = await rd.smembers(processing_key)

                for uid in stuck_applicants:
                    await rd.sadd(key, uid)

            await rd.delete(processing_key)

@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = AsyncIOScheduler()
    scheduler.add_job(move_redis_to_db_task, 'interval', seconds=10)
    scheduler.start()

    yield

    scheduler.shutdown()
    await rd.close()

app = FastAPI(
    title="Find a Needle",
    description="Node.js와 협업하는 하이브리드 추첨 시스템",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

@app.get("/", tags=["System"])
async def root():
    return {
        "project": "Find a Needle",
        "status": "online",
        "engine": "FastAPI + Redis + PostgreSQL"
    }

@app.get("/health", tags=["System"])
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "redis_connected": rd is not None
    }