from datetime import datetime
from pydantic import BaseModel


class AuthBase(BaseModel):
    user_id: str


class AuthCreate(AuthBase):
    pass


class AuthResponse(AuthBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
