from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.status import HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR, HTTP_409_CONFLICT
from config.exceptions import NotFoundError, SpendServiceError, SpendIntegrityServiceError

async def not_found_error_handler(request: Request, exc: NotFoundError):
    return JSONResponse(
        status_code=HTTP_404_NOT_FOUND,
        content={"detail": exc.user_message},
    )

async def internal_server_error(request: Request, exc: SpendServiceError):
    return JSONResponse(
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": exc.user_message},
    )

async def duplicate_category(request: Request, exc: SpendIntegrityServiceError):
    return JSONResponse(
        status_code=HTTP_409_CONFLICT,
        content={"detail": exc.user_message},
    )
