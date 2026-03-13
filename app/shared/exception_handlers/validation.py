# app/shared/exception_handlers/validation.py
from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from ..schemas import ErrorResponse
from ..logging import get_logger


logger = get_logger(__name__)


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Handle ``RequestValidationError`` and return a uniform ``ErrorResponse`` body.

    Converts Pydantic validation errors raised during request parsing into
    the application's standard error envelope. The raw error list from
    Pydantic is serialized to a string and included in ``detail`` so the
    client can identify which fields failed validation and why.

    Logged at ``WARNING`` level since validation failures reflect invalid
    client input rather than an application fault.

    Parameters
    ----------
    request : Request
        Incoming request that triggered the exception. Used to include
        the request method and URL in the log record for easier debugging.
    exc : RequestValidationError
        The caught exception carrying the list of Pydantic validation errors.

    Returns
    -------
    JSONResponse
        JSON-encoded ``ErrorResponse`` with status code ``422``.
    """

    logger.warning(
        "Validation error",
        extra={
            "method": request.method,
            "url": str(request.url),
            "errors": exc.errors(),
        },
    )
    error = exc.errors()[0]
    detail = str(error.get("ctx", {}).get("error", error["msg"])) if exc.errors() else "Validation error."
    body = ErrorResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        error="Unprocessable Entity",
        detail=str(detail),
    )
    return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, content=body.model_dump())