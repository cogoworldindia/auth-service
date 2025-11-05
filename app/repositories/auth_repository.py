from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.auth_data_model import AuthData, ProviderType
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException


class AuthRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_email(self, email: str):
        """
        Fetch the AuthData record by email for provider EMAIL.
        """
        stmt = select(AuthData).where(
            AuthData.auth_identifier == email,
            AuthData.provider_type == ProviderType.EMAIL
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, email: str, auth_account_id: int = 0, auth_type_id: int = 0):
        """
        Create new AuthData entry for email-based authentication.
        """
        try:
            new_auth_data = AuthData(
                auth_account_id=auth_account_id,  # TODO: replace 0 with actual auth.id when available
                auth_type_id=auth_type_id,     # TODO: replace 0 with actual auth_type.id for EMAIL
                provider_type=ProviderType.EMAIL,
                auth_identifier=email,
                is_verified=True,
            )
            self.db.add(new_auth_data)
            await self.db.commit()
            await self.db.refresh(new_auth_data)
            return new_auth_data
        except IntegrityError:
            await self.db.rollback()
            raise HTTPException(status_code=400, detail="Auth record already exists")

    async def update_verification_status(self, email: str, is_verified: bool = True):
        """
        Update the verification status of a user by email.
        """
        stmt = select(AuthData).where(
            AuthData.auth_identifier == email,
            AuthData.provider_type == ProviderType.EMAIL
        )
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        user.is_verified = is_verified
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def delete_by_email(self, email: str):
        """
        Delete auth data by email (for cleanup).
        """
        stmt = select(AuthData).where(
            AuthData.auth_identifier == email,
            AuthData.provider_type == ProviderType.EMAIL
        )
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()
        if user:
            await self.db.delete(user)
            await self.db.commit()
            return True
        return False
