from typing import Optional, Any
from pydantic import BaseModel

class ResponseSchema(BaseModel):
    status: str                   # "success" | "error"
    code: int                     # custom app-level code (e.g. 2000 for success, 4001 for validation error)
    message: Optional[str] = None
    data: Optional[Any] = None
    error: Optional[Any] = None

    class Config:
        from_attributes = True
