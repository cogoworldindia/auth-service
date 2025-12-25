from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.services.google_auth_service import AuthService
from app.utils.response_helper import error_response, success_response
from fastapi.encoders import jsonable_encoder

router = APIRouter(prefix="", tags=["Google Auth"])

@router.post("/")
async def google_signup(id_token: str, db: AsyncSession = Depends(get_db)):
    try:
        if not id_token:
            return error_response(
                        message="Missing Google ID token",
                        code=400,
                    )

        service = AuthService(db)
        result = await service.signup_with_google(id_token)
        return success_response(
                    message="Google signup successful",
                    data=jsonable_encoder(result),
                    code=200,
                )
    except Exception as e:
            return error_response(
                    message="Invalid Google ID token",
                    error=str(e),
                    http_status=401,
                    code=401
                )