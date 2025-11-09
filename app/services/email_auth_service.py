from fastapi import HTTPException
import httpx
from app.utils.email_client import send_verification_email
from app.utils.verification import create_email_verification, verify_email_code
from app.core.config import settings
from app.repositories.auth_repository import AuthRepository
from app.utils.jwt_utils import create_access_token
from app.utils.http_client import async_post


class EmailAuthService:
    def __init__(self, db):
        self.repo = AuthRepository(db)

    async def send_verification(self, email: str):
        code = await create_email_verification(email)
        subject = "Verify your CoGo Account"
        body = f"<h3>Your verification code is: <b>{code}</b></h3>"

        await send_verification_email(email, subject, body)
        return {"message": "Verification email sent"}

    async def verify_code(self, email: str, code: str):
        """
        Verifies email, creates user in user-service if not exists,
        and creates local auth + auth_data records.
        """
        try:
            # is_valid = await verify_email_code(email, code)
            is_valid = True  # Replace with your verify_email_code(email, code)
            if not is_valid:
                raise HTTPException(status_code=400, detail="Invalid or expired verification code")

            # ---- Check existing user in local DB ----
            user = await self.repo.get_by_email(email)

            # ---- Create new user via user-service if not found ----
            if not user:
                user_response = await async_post(
                    f"{settings.USER_SERVICE_URL}/user",
                    json={"status": "active"},
                )

                if not user_response or user_response.status_code != 200:
                    raise HTTPException(status_code=500, detail="User creation failed")

                user_data = user_response.json()
                user_id = user_data["data"]["id"]

                # Create new local auth + auth_data entries
                user = await self.repo.create(email, user_id, auth_type_id=1)
            else:
                print("User already exists locally.", user.user_id)
                user_id = user.user_id

            # ---- Generate JWT ----
            token = create_access_token({"user_id": user_id, "email": email})

            return {"access_token": token, "token_type": "bearer", "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60}

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Auth error: {str(e)}")
