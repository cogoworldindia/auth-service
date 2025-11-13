from fastapi import HTTPException
import httpx
from app.utils.email_client import send_verification_email
from app.utils.verification import create_email_verification, verify_email_code
from app.core.config import settings
from app.repositories.auth_repository import AuthRepository
from app.utils.jwt_utils import create_access_token
from app.services.token_service import TokenService
from app.utils.http_client import async_post
from app.services.user_provisioning_service import UserProvisioningService
from app.models.auth_data_model import ProviderType


class EmailAuthService:
    def __init__(self, db):
        self.repo = AuthRepository(db)

    async def send_verification(self, email: str):
        try:
            code = await create_email_verification(email)
            subject = "Verify your CoGo Account"
            body = f"<h3>Your verification code is: <b>{code}</b></h3>"
            await send_verification_email(email, subject, body)
            return {"message": "Verification email sent"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error sending verification email: {str(e)}")

    async def verify_code(self, email: str, code: str):
        """
        Verifies email, creates user in user-service if not exists,
        and creates local auth + auth_data records.
        """
        try:
            is_valid = await verify_email_code(email, code)
            if not is_valid:
                raise HTTPException(status_code=400, detail="Invalid or expired verification code")

            # ---- Ensure user and local auth via reusable provisioning ----
            provisioning = UserProvisioningService(self.repo.db)
            user = await provisioning.ensure_user_and_auth(
                provider=ProviderType.EMAIL,
                identifier=email,
                default_auth_type_id=1,
                is_verified=True,
                user_status_payload={"status": "active"},
            )
            user_id = user.user_id

            # ---- Generate Tokens (access + refresh) ----
            access_token = create_access_token({"user_id": user_id, "email": email})
            token_service = TokenService()
            refresh_token = await token_service.generate_refresh_token(
                user_id=str(user_id),
                metadata={"email": email}
            )

            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
                "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
            }

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Auth error: {str(e)}")
