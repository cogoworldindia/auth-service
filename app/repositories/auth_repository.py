from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.auth_data_model import AuthData, ProviderType
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from app.models.auth_model import Auth


class AuthRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_identifier(self, provider: ProviderType, identifier: str):
        """
        Generic fetch by provider and identifier.
        """
        stmt = (
            select(Auth)
            .join(AuthData)
            .where(
                AuthData.auth_identifier == identifier,
                # AuthData.provider_type == provider,
            )
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def get_by_email(self, email: str):
        """
        Fetch the Auth record associated with given email for provider EMAIL.
        """
        stmt = (
            select(Auth)
            .join(AuthData)
            .where(
                AuthData.auth_identifier == email,
                AuthData.provider_type == ProviderType.EMAIL
            )
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()  # returns Auth object or None

    async def create_for_identifier(
        self,
        user_id: str,
        auth_type_id: int,
        provider: ProviderType,
        identifier: str,
        is_verified: bool = True,
    ):
        """
        Generic create for any provider + identifier.
        """
        try:
            auth = Auth(user_id=user_id)
            self.db.add(auth)
            await self.db.flush()  # get auth.id

            auth_data = AuthData(
                auth_account_id=auth.id,
                auth_type_id=auth_type_id,
                provider_type=provider,
                auth_identifier=identifier,
                is_verified=is_verified,
            )
            self.db.add(auth_data)

            await self.db.commit()
            await self.db.refresh(auth)
            return auth
        except IntegrityError:
            await self.db.rollback()
            raise HTTPException(status_code=400, detail="Auth record already exists")

    async def create(self, email: str, user_id: str, auth_type_id: int):
        """
        Create new AuthData entry for email-based authentication.
        """
        try:
            auth = Auth(user_id=user_id)
            self.db.add(auth)
            await self.db.flush()  # get auth.id

            auth_data = AuthData(
                auth_account_id=auth.id,
                auth_type_id=auth_type_id,
                provider_type=ProviderType.EMAIL,
                auth_identifier=email,
                is_verified=True,
            )
            self.db.add(auth_data)

            await self.db.commit()
            await self.db.refresh(auth)
            return auth
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
