from fastapi.responses import JSONResponse
from app.schemas.response_schema import ResponseSchema

def success_response(
    message: str = "Success",
    data: any = None,
    http_status: int = 200,
    code: int = 200,  # custom success code
):
    return JSONResponse(
        status_code=http_status,
        content=ResponseSchema(
            status="success",
            code=code,
            message=message,
            data=data,
            error=None
        ).model_dump()
    )


def error_response(
    message: str = "Error",
    error: any = None,
    http_status: int = 400,
    code: int = 400,  # custom error code
):
    return JSONResponse(
        status_code=http_status,
        content=ResponseSchema(
            status="error",
            code=code,
            message=message,
            data=None,
            error=error
        ).model_dump()
    )
