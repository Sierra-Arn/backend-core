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