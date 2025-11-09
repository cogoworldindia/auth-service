from fastapi import APIRouter, HTTPException, Depends
from app.services.email_auth_service import EmailAuthService
from app.db.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.response_helper import success_response, error_response
from fastapi.encoders import jsonable_encoder

router = APIRouter(prefix="", tags=["Email Auth"])


@router.post("/send")
async def send_verification(email: str, db: AsyncSession = Depends(get_db)):
    try:
        service = EmailAuthService(db)
        response = await service.send_verification(email)
        return success_response(
                message="OTP sent successfully",
                data=jsonable_encoder(response),
                code=200,
            )
    except Exception as e:
        return error_response(
                message="Failed to create user",
                error=str(e),
                http_status=500,
                code=500
            )


@router.post("/verify")
async def verify_code(email: str, code: str, db: AsyncSession = Depends(get_db)):
    try:
        service = EmailAuthService(db)
        response = await service.verify_code(email, code)
        return success_response(
                    message="Successfully verified OTP",
                    data=jsonable_encoder(response),
                    code=200,
                )
    except Exception as e:
        return error_response(
                    message="Failed to verify OTP",
                    error=str(e),
                    http_status=500,
                    code=500
                )