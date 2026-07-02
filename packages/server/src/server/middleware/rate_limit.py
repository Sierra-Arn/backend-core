# Copyright (c) 2026 Ilya Snegov (aka Sierra Arn)

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# packages/server/src/server/middleware/rate_limit.py
import logging
from fastapi import status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from rate_limit_lib import RateLimitService
from schemas_lib import ErrorResponse

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware that enforces IP-based rate limiting on every incoming request.

    On each request the client IP address is extracted and checked against
    the sliding window counter stored in Redis. If the limit is exceeded the
    request is rejected immediately with 429 Too Many Requests before it
    reaches any route handler.

    Rate limit parameters — maximum requests and window duration — are read
    from redis_config at startup and require an application restart to take
    effect.

    Notes
    -----
    BaseHTTPMiddleware wraps every request in a try/except block internally,
    so unhandled exceptions raised inside dispatch are still caught by the
    global exception handlers registered on the application.
    """

    async def dispatch(self, request: Request, call_next: callable) -> Response:
        """
        Check the rate limit for the incoming request and either forward it
        or reject it with a 429 response.

        Parameters
        ----------
        request : Request
            Incoming HTTP request.
        call_next : callable
            Next handler in the middleware chain. Called only if the rate
            limit has not been exceeded.

        Returns
        -------
        Response
            Response from the next handler if the request is allowed, or a
            429 Too Many Requests JSON response if the limit is exceeded.
        """
        ip = request.client.host

        if not await RateLimitService.is_allowed(ip):
            logger.warning(
                "Rate limit exceeded",
                extra={
                    "ip": ip,
                    "method": request.method,
                    "url": str(request.url),
                },
            )
            body = ErrorResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                error="Too Many Requests",
                detail="Rate limit exceeded.",
            )
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content=body.model_dump(),
            )

        return await call_next(request)