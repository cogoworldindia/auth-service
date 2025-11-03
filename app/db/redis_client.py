import redis.asyncio as aioredis
from app.core.config import settings

redis = None  # Global client instance


async def init_redis():
    """Initialize and return a global Redis connection."""
    global redis
    if redis is None:
        redis = await aioredis.from_url(
            settings.REDIS_URL,
            decode_responses=True,  # optional, depending on how you store data
        )
    return redis


async def get_redis():
    """Get the initialized Redis client."""
    if redis is None:
        return await init_redis()
    return redis


async def close_redis():
    """Gracefully close Redis connection."""
    global redis
    if redis:
        await redis.close()
        redis = None
