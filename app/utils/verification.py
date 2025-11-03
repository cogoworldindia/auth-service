import secrets
import json
from datetime import timedelta
import redis.asyncio as aioredis
from app.db.redis_client import get_redis
from app.core.config import settings


async def create_email_verification(email: str):
    """Generate and store verification code in Redis."""
    redis = await get_redis()
    code = secrets.token_urlsafe(6)[:6].upper()
    key = f"verify:email:{email}"
    data = {"email": email, "code": code}
    await redis.set(key, json.dumps(data), ex=600)  # expires in 10 min
    await redis.close()
    return code


async def verify_email_code(email: str, code: str):
    """Check if code is valid."""
    redis = await get_redis()
    key = f"verify:email:{email}"
    data = await redis.get(key)
    if not data:
        await redis.close()
        return False
    stored = json.loads(data)
    if stored["code"] == code:
        await redis.delete(key)
        await redis.close()
        return True
    await redis.close()
    return False
