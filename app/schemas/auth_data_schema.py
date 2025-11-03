from datetime import datetime
from enum import Enum
from pydantic import BaseModel


class ProviderType(str, Enum):
    GOOGLE = "google"
    APPLE = "apple"
    FACEBOOK = "facebook"
    EMAIL = "email"
    PHONE = "phone"


class AuthDataBase(BaseModel):
    provider_type: ProviderType
    auth_identifier: str
    is_verified: bool = False


class AuthDataCreate(AuthDataBase):
    auth_account_id: int
    auth_type_id: int


class AuthDataResponse(AuthDataBase):
    id: int
    auth_account_id: int
    auth_type_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
