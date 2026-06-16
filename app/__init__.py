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

# app/__init__.py
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from .config import api_config
from .shared.exception_handlers import (
    validation_exception_handler, 
    http_exception_handler, 
    unhandled_exception_handler
)
from .shared.middleware import RateLimitMiddleware, AccessLogMiddleware
from .modules import (
    auth_router, 
    account_router, 
    health_router, 
    users_router, 
    roles_router
)

def create_app() -> FastAPI:
    """Create and configure FastAPI application."""

    app = FastAPI(
        title=api_config.title,
        description=api_config.description,
        version=api_config.version,
        docs_url=api_config.docs_url,
        redoc_url=api_config.redoc_url,
        openapi_url=api_config.openapi_url
    )

    app.include_router(auth_router)
    app.include_router(account_router)
    app.include_router(health_router)
    app.include_router(users_router)
    app.include_router(roles_router)

    # Order matters: handlers must be registered from most specific to most general.
    # FastAPI matches the first handler whose exception type matches or is a parent
    # of the raised exception. Registering Exception first would cause it to
    # intercept both HTTPException and RequestValidationError before their
    # dedicated handlers have a chance to run.
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)

    # Middleware is applied in reverse registration order — the last registered
    # middleware wraps the outermost layer of the request. AccessLogMiddleware
    # is registered first so that it runs last, ensuring it captures the final
    # response status code after all other middleware has processed the request.
    app.add_middleware(AccessLogMiddleware)
    app.add_middleware(RateLimitMiddleware)

    return app