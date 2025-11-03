from pydantic import BaseModel
from typing import Optional


class AuthTypeBase(BaseModel):
    type: str
    description: Optional[str]


class AuthTypeCreate(AuthTypeBase):
    pass


class AuthTypeResponse(AuthTypeBase):
    id: int

    class Config:
        orm_mode = True
