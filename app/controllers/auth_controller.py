from fastapi import APIRouter, Depends, Header, HTTPException, status
from app.utils.jwt_utils import verify_access_token
from app.services.auth_service import AuthService
from app.utils.response_helper import success_response, error_response
from fastapi.encoders import jsonable_encoder
router = APIRouter(prefix="", tags=["Validate Token"])


@router.get("")
async def validate_access_token(authorization: str = Header(None)):
    try:
        """
        Validates JWT access token and returns the user_id.
        """
        if not authorization:
            return error_response(
                message="Missing Authorization header",
                error="Missing Authorization header",
                http_status=status.HTTP_401_UNAUTHORIZED,
                code=401
            )

        # Accept 'Bearer <token>' or just '<token>'
        parts = authorization.split(" ")
        token = parts[1] if len(parts) == 2 and parts[0].lower() == "bearer" else parts[0]

        service = AuthService()
        response = await service.validate_token(token)
        return success_response(
                message="Token is valid",
                data=jsonable_encoder(response),
                code=200,
            )
    
    except HTTPException as e:
        return error_response(
                message="Authorization failed",
                error=str(e),
                http_status=401,
                code=401
            )
