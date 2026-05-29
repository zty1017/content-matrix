from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from backend.app.core.errors import DomainError


def handle_domain_error(_: Request, exc: DomainError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content=exc.to_payload())


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(DomainError, handle_domain_error)
