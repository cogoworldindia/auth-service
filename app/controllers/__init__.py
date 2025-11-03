from fastapi import APIRouter
# Create a master router that includes all route modules
from app.controllers import auth_controller, token_controller

router = APIRouter()
