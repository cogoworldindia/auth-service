from fastapi import APIRouter, HTTPException, Depends
from app.services.email_auth_service import EmailAuthService
from app.db.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/email", tags=["Email Auth"])


@router.post("/send")
async def send_verification(email: str, db: AsyncSession = Depends(get_db)):
    try:
        service = EmailAuthService(db)
        return await service.send_verification(email)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/verify")
async def verify_code(email: str, code: str, db: AsyncSession = Depends(get_db)):
    try:
        service = EmailAuthService(db)
        return await service.verify_code(email, code)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))