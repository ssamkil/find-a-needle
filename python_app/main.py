import os
import sentry_sdk
from contextlib import asynccontextmanager
from fastapi import FastAPI
from sentry_sdk.integrations.fastapi import FastApiIntegration
from apscheduler.schedulers.background import BackgroundScheduler

# 절대 경로 임포트 (python_app 명칭 사용)
from python_app.db.session import engine, Base
from python_app.api.api import api_router

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    integrations=[FastApiIntegration()],
    traces_sample_rate=1.0,
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    scheduler = BackgroundScheduler()
    scheduler.start()

    yield

    scheduler.shutdown()

app = FastAPI(
    title="Find A Needle",
    lifespan=lifespan
)

app.include_router(api_router, prefix="/api")

@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "ok"}