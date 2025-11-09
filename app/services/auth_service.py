from fastapi import HTTPException, status
from app.utils.jwt_utils import verify_access_token


class AuthService:
    """
    Handles token validation and authentication-related logic.
    """

    async def validate_token(self, token: str):
        """
        Validates the JWT access token and returns its payload (claims).
        """
        try:
            payload = verify_access_token(token)
            if not payload or "user_id" not in payload:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid token payload",
                )
            return payload

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Token validation failed: {str(e)}",
            )
