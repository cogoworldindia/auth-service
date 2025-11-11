from fastapi import HTTPException, status
from firebase_admin import auth as firebase_auth
from app.utils.http_client import async_post
from app.utils.jwt_utils import create_access_token
from app.repositories.auth_repository import AuthRepository
from app.core.config import settings
from app.services.user_provisioning_service import UserProvisioningService
from app.models.auth_data_model import ProviderType
from app.services.token_service import TokenService


class AuthService:
    def __init__(self, db_session=None):
        self.repo = AuthRepository(db_session) if db_session else None

    async def signup_with_google(self, id_token: str):
        """
        Verifies Google ID token via Firebase, creates or retrieves Auth record,
        and returns an access token.
        """
        try:
            # Verify token via Firebase Admin
            decoded = firebase_auth.verify_id_token(id_token)
            email = decoded.get("email")
            email_verified = decoded.get("email_verified")
            uid = decoded.get("uid")

            if not email or not email_verified:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid or unverified Google account"
                )

            # ---- Ensure user and local auth via reusable provisioning ----
            provisioning = UserProvisioningService(self.repo.db)
            user = await provisioning.ensure_user_and_auth(
                provider=ProviderType.GOOGLE,
                identifier=email,
                default_auth_type_id=3,
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

        except firebase_auth.InvalidIdTokenError:
            raise HTTPException(status_code=401, detail="Invalid Google ID token")
        except firebase_auth.ExpiredIdTokenError:
            raise HTTPException(status_code=401, detail="Expired Google ID token")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Google signup failed: {str(e)}")
