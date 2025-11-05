from fastapi import HTTPException
import httpx
from app.utils.email_client import send_verification_email
from app.utils.verification import create_email_verification, verify_email_code
from app.core.config import settings
from app.repositories.auth_repository import AuthRepository
from app.utils.jwt_utils import create_access_token


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
        is_valid = await verify_email_code(email, code)
        if not is_valid:
            raise HTTPException(status_code=400, detail="Invalid or expired verification code")

        user = await self.repo.get_by_email(email)

        if not user:
            async with httpx.AsyncClient(timeout=20.0) as client:
                response = await client.post(
                    f"{settings.USER_SERVICE_URL}/users",
                    json={"email": email}
                )
                if response.status_code != 201:
                    raise HTTPException(status_code=500, detail="User creation failed")
                user_data = response.json()
                user_id = user_data["id"]

            user = await self.repo.create(email, user_id, auth_type_id=1)  # Assuming 1 is the ID for EMAIL auth type
        else:
            user_id = user.user_id

        token = create_access_token({"user_id": user_id, "email": email})
        return {"access_token": token, "token_type": "bearer"}
