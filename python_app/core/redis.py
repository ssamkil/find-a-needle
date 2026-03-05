import redis.asyncio as redis
from python_app.core.config import settings

rd = redis.from_url(settings.REDIS_URL, decode_responses=True)