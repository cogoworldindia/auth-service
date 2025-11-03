from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel


class SessionAction(str, Enum):
    LOGIN = "login"
    LOGOUT = "logout"
    PASSWORD_CHANGE = "password_change"


class SessionAuditBase(BaseModel):
    action: SessionAction
    ip_address: Optional[str]
    user_agent: Optional[str]


class SessionAuditCreate(SessionAuditBase):
    auth_id: int


class SessionAuditResponse(SessionAuditBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
