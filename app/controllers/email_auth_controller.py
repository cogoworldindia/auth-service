from fastapi import APIRouter, HTTPException
from app.utils.email_client import send_verification_email
from app.utils.verification import create_email_verification, verify_email_code

router = APIRouter(prefix="/email", tags=["Email Auth"])


@router.post("/send")
async def send_verification(email: str):
    code = await create_email_verification(email)
    subject = "Verify your CoGo Account"
    body = f"<h3>Your verification code is: <b>{code}</b></h3>"
    await send_verification_email(email, subject, body)
    return {"message": "Verification email sent"}


@router.post("/verify")
async def verify_code(email: str, code: str):
    is_valid = await verify_email_code(email, code)
    if not is_valid:
        raise HTTPException(status_code=400, detail="Invalid or expired verification code")
    # Here you can mark the user as verified in DB
    return {"message": "Email verified successfully"}
