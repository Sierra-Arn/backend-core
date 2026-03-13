# app/shared/exception_handlers/unhandled.py
from fastapi import Request
from fastapi.responses import JSONResponse
from ..schemas import ErrorResponse
from ..logging import get_logger


logger = get_logger(__name__)


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Catch-all handler for any exception not handled by a more specific handler.

    Logs the full traceback at ``ERROR`` level so the failure can be
    investigated, then returns a generic ``500`` response to the client
    without exposing any internal details.

    Parameters
    ----------
    request : Request
        Incoming request that triggered the exception. Used to include
        the request method and URL in the log record for easier debugging.
    exc : Exception
        The unhandled exception.

    Returns
    -------
    JSONResponse
        JSON-encoded ``ErrorResponse`` with status code ``500``.
    """

    logger.error(
        "Unhandled exception",
        exc_info=exc,
        extra={
            "method": request.method,
            "url": str(request.url),
        },
    )
    body = ErrorResponse(
        status_code=500,
        error="Internal Server Error",
        detail="Internal server error",
    )
    return JSONResponse(status_code=500, content=body.model_dump())