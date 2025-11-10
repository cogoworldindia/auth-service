from typing import Optional
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.repositories.auth_repository import AuthRepository
from app.models.auth_data_model import ProviderType
from app.utils.http_client import async_post


class UserProvisioningService:
    """
    Orchestrates user creation in user-service and local auth/auth_data linking,
    reusable across providers (email, phone, google, etc.).
    """

    def __init__(self, db: AsyncSession):
        self.repo = AuthRepository(db)

    async def ensure_user_and_auth(
        self,
        provider: ProviderType,
        identifier: str,
        default_auth_type_id: int,
        is_verified: bool = True,
        user_status_payload: Optional[dict] = None,
    ):
        """
        1) Find local auth by provider+identifier.
        2) If not found, ensure remote user exists via user-service and create local records.
        Returns the local Auth row.
        """
        # Step 1: local lookup
        auth = await self.repo.get_by_identifier(provider, identifier)
        if auth:
            return auth

        # Step 2: create remote user
        payload = user_status_payload or {"status": "active"}
        user_response = await async_post(
            f"{settings.USER_SERVICE_URL}/user",
            json=payload,
        )

        if not user_response or user_response.status_code != 200:
            raise HTTPException(status_code=500, detail="User creation failed")

        user_data = user_response.json()
        user_id = str(user_data["data"]["id"])

        # Step 3: create local records
        auth = await self.repo.create_for_identifier(
            user_id=user_id,
            auth_type_id=default_auth_type_id,
            provider=provider,
            identifier=identifier,
            is_verified=is_verified,
        )
        return auth


