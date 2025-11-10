import json
import secrets
from datetime import timedelta
from typing import Any, Dict, Optional
from app.core.config import settings
from app.db.redis_client import get_redis
from app.utils.jwt_utils import create_access_token


class TokenService:
    async def _build_refresh_key(self, token: str) -> str:
        return f"{settings.REFRESH_TOKEN_REDIS_PREFIX}{token}"

    async def generate_refresh_token(
        self,
        user_id: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Create an opaque refresh token and store it in Redis with TTL.
        Value stored: JSON with user_id and optional metadata.
        """
        refresh_token = secrets.token_urlsafe(48)
        key = await self._build_refresh_key(refresh_token)
        redis = await get_redis()
        value = {
            "user_id": user_id,
            "metadata": metadata or {},
        }
        ttl_seconds = int(timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS).total_seconds())
        await redis.set(key, json.dumps(value), ex=ttl_seconds)
        return refresh_token

    async def validate_refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Validate refresh token by checking Redis; returns stored payload.
        Raises ValueError if not found/expired.
        """
        key = await self._build_refresh_key(refresh_token)
        redis = await get_redis()
        data = await redis.get(key)
        if not data:
            raise ValueError("Invalid or expired refresh token")
        try:
            return json.loads(data)
        except Exception:
            raise ValueError("Corrupted refresh token data")

    async def revoke_refresh_token(self, refresh_token: str) -> None:
        key = await self._build_refresh_key(refresh_token)
        redis = await get_redis()
        await redis.delete(key)

    async def rotate_refresh_token(
        self,
        refresh_token: str,
        user_id: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Delete old refresh token record and issue a new one.
        """
        await self.revoke_refresh_token(refresh_token)
        return await self.generate_refresh_token(user_id=user_id, metadata=metadata)

    async def issue_token_pair(
        self,
        user_id: str,
        email: Optional[str] = None,
        scope: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Helper: generate access and refresh tokens together.
        """
        access_token = create_access_token(
            {
                "user_id": user_id,
                **({"email": email} if email else {}),
                **({"scope": scope} if scope else {}),
            }
        )
        refresh_token = await self.generate_refresh_token(user_id=user_id, metadata=metadata)
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
        }


