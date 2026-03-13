# app/shared/middleware/access_log.py
import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from ..logging import get_logger


access_logger = get_logger("access")


class AccessLogMiddleware(BaseHTTPMiddleware):
    """
    Middleware that logs every incoming HTTP request and its outcome.

    Captures the request method, URL, client IP, HTTP status code, and
    response time for every request that passes through the application.
    All records are emitted at ``INFO`` level under the ``"access"`` logger,
    which allows them to be filtered separately from internal system logs
    by the ``type`` field in the JSON output.

    Notes
    -----
    Response time is measured from the moment ``dispatch`` is entered to
    the moment the response object is returned by the next handler. It
    does not include the time spent streaming the response body to the client.
    """

    async def dispatch(self, request: Request, call_next: callable) -> Response:
        """
        Record the request, delegate to the next handler, and log the result.

        Parameters
        ----------
        request : Request
            Incoming HTTP request.
        call_next : callable
            Next handler in the middleware chain.

        Returns
        -------
        Response
            The response returned by the next handler, passed through unchanged.
        """
        start = time.perf_counter()
        response: Response = await call_next(request)
        response_time_ms = round((time.perf_counter() - start) * 1000, 2)

        access_logger.info(
            "Request handled",
            extra={
                "type": "access",
                "ip": request.client.host,
                "method": request.method,
                "url": str(request.url),
                "status_code": response.status_code,
                "response_time_ms": response_time_ms,
            },
        )

        return response