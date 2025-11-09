from fastapi import APIRouter
# Create a master router that includes all route modules
from app.controllers import email_auth_controller, auth_controller

router = APIRouter()
router.include_router(email_auth_controller.router, prefix="/email", tags=["Email Auth"])
router.include_router(auth_controller.router, prefix="/validate", tags=["Validate Token"])
