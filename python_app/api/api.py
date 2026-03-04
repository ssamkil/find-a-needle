from fastapi import APIRouter
from python_app.api.endpoints import auth, events, apply, draw

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(events.router, prefix="/events", tags=["Events"])
api_router.include_router(apply.router, prefix="/apply", tags=["Application"])
api_router.include_router(draw.router, prefix="/draw", tags=["Lottery Management"])