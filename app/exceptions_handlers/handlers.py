from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.status import HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR
from config.exceptions import NotFoundError, SpendServiceError

async def not_found_error_handler(request: Request, exc: NotFoundError):
    return JSONResponse(
        status_code=HTTP_404_NOT_FOUND,
        content={"detail": str(exc)},
    )

async def internal_server_error(request: Request, exc: SpendServiceError):
    return JSONResponse(
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Erro interno na aplicação. Consulte o administrador!"},
    )

