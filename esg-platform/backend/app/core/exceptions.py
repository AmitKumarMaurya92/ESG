"""
Centralised exception handlers and custom exception classes.

All HTTP error responses use the structured format:

    {"error": {"code": "SNAKE_CASE_CODE", "message": "Human-readable message"}}

Internal stack traces are never exposed to API clients.
"""

import logging
from typing import Any, Dict, Optional

from fastapi import HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


# ── Custom exception hierarchy ────────────────────────────────────────────────

class ESGBaseException(Exception):
    """Base class for all application-level exceptions."""

    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    error_code: str = "INTERNAL_ERROR"
    message: str = "An unexpected error occurred."

    def __init__(self, message: Optional[str] = None, **kwargs: Any) -> None:
        self.message = message or self.__class__.message
        self.extra = kwargs
        super().__init__(self.message)


class NotFoundError(ESGBaseException):
    status_code = status.HTTP_404_NOT_FOUND
    error_code = "NOT_FOUND"
    message = "The requested resource was not found."


class AuthenticationError(ESGBaseException):
    status_code = status.HTTP_401_UNAUTHORIZED
    error_code = "AUTHENTICATION_ERROR"
    message = "Authentication is required."


class AuthorizationError(ESGBaseException):
    status_code = status.HTTP_403_FORBIDDEN
    error_code = "AUTHORIZATION_ERROR"
    message = "You do not have permission to perform this action."


class ValidationError(ESGBaseException):
    status_code = status.HTTP_422_UNPROCESSABLE_CONTENT
    error_code = "VALIDATION_ERROR"
    message = "The request data is invalid."


class ConflictError(ESGBaseException):
    status_code = status.HTTP_409_CONFLICT
    error_code = "CONFLICT"
    message = "A conflict occurred with the current state of the resource."


class TenantIsolationError(ESGBaseException):
    """Raised when a cross-tenant data access attempt is detected."""
    status_code = status.HTTP_403_FORBIDDEN
    error_code = "TENANT_ISOLATION_VIOLATION"
    message = "Access denied: cross-tenant data access is not permitted."


class RateLimitError(ESGBaseException):
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    error_code = "RATE_LIMIT_EXCEEDED"
    message = "Too many requests. Please slow down."


# ── Response helper ───────────────────────────────────────────────────────────

def error_response(code: str, message: str, status_code: int) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"error": {"code": code, "message": message}},
    )


# ── FastAPI exception handlers ────────────────────────────────────────────────

async def esg_exception_handler(request: Request, exc: ESGBaseException) -> JSONResponse:
    logger.warning(
        "Application exception: code=%s message=%s path=%s",
        exc.error_code,
        exc.message,
        request.url.path,
    )
    return error_response(exc.error_code, exc.message, exc.status_code)


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    code = "HTTP_ERROR"
    message = exc.detail if isinstance(exc.detail, str) else str(exc.detail)
    return error_response(code, message, exc.status_code)


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    # Flatten Pydantic v2 validation errors into a readable string
    errors = []
    for error in exc.errors():
        loc = " → ".join(str(p) for p in error.get("loc", []))
        errors.append(f"{loc}: {error.get('msg', 'Invalid value')}")
    message = "; ".join(errors)
    logger.debug("Validation error on %s: %s", request.url.path, message)
    return error_response("VALIDATION_ERROR", message, status.HTTP_422_UNPROCESSABLE_CONTENT)


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    # Log full traceback internally; never expose to client
    logger.exception("Unhandled exception on %s", request.url.path)
    return error_response(
        "INTERNAL_ERROR",
        "An unexpected error occurred. Please try again later.",
        status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
