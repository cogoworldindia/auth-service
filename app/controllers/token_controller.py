from fastapi import APIRouter, HTTPException
from app.schemas.token_schema import RefreshTokenRequest, TokenPairResponse
from app.services.token_service import TokenService
from app.utils.response_helper import success_response, error_response
from app.utils.jwt_utils import create_access_token
from app.core.config import settings
from datetime import timedelta
from fastapi.encoders import jsonable_encoder

router = APIRouter(prefix="/token", tags=["Token"])


@router.post("/refresh")
async def refresh_token(payload: RefreshTokenRequest):
    try:
        svc = TokenService()
        stored = await svc.validate_refresh_token(payload.refresh_token)
        user_id = stored.get("user_id")
        if not user_id:
            raise HTTPException(status_code=400, detail="Invalid token payload")

        # Rotate refresh token
        new_refresh_token = await svc.rotate_refresh_token(
            payload.refresh_token,
            user_id=user_id,
            metadata=stored.get("metadata") or {},
        )

        # Issue new access token
        access_token = create_access_token(
            {"user_id": user_id},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        )

        response = TokenPairResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )
        return success_response(
            message="Token refreshed",
            data=jsonable_encoder(response),
            code=200,
        )
    except HTTPException as e:
        return error_response(
            message="Failed to refresh token",
            error=str(e.detail) if hasattr(e, "detail") else str(e),
            http_status=e.status_code if hasattr(e, "status_code") else 400,
            code=e.status_code if hasattr(e, "status_code") else 400,
        )
    except Exception as e:
        return error_response(
            message="Failed to refresh token",
            error=str(e),
            http_status=500,
            code=500,
        )

