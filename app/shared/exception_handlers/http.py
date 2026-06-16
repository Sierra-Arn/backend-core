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

# app/shared/exception_handlers/http.py
from fastapi import Request
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from http import HTTPStatus
from ..schemas import ErrorResponse
from ..logging import get_logger


logger = get_logger(__name__)


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    Handle ``HTTPException`` and return a uniform ``ErrorResponse`` body.

    Converts the HTTP status code to its standard phrase (e.g., ``404``
    to ``"Not Found"``) and packages it alongside the exception detail
    into the application's standard error envelope.

    Client errors (``4xx``) are logged at ``WARNING`` level since they
    reflect invalid client behavior rather than an application fault.
    Server errors (``5xx``) are logged at ``ERROR`` level since they
    indicate a problem within the application itself.

    Parameters
    ----------
    request : Request
        Incoming request that triggered the exception. Used to include
        the request method and URL in the log record for easier debugging.
    exc : HTTPException
        The caught exception carrying ``status_code`` and ``detail``.

    Returns
    -------
    JSONResponse
        JSON-encoded ``ErrorResponse`` with the matching HTTP status code.
    """

    phrase = HTTPStatus(exc.status_code).phrase
    log_extra = {
        "method": request.method,
        "url": str(request.url),
        "status_code": exc.status_code,
        "detail": exc.detail,
    }

    if exc.status_code >= 500:
        logger.error("HTTP error", extra=log_extra)
    else:
        logger.warning("HTTP error", extra=log_extra)

    body = ErrorResponse(
        status_code=exc.status_code,
        error=phrase,
        detail=exc.detail,
    )
    return JSONResponse(status_code=exc.status_code, content=body.model_dump())