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

# app/modules/auth/register/routes.py
from fastapi import status
from .schemas import RegisterRequest
from .domen import register
from ..router import auth_router

# Route registration: decorating with @auth_router.post() alone is not enough —
# this module must be imported somewhere in the application (e.g., in
# app/modules/auth/__init__.py) for FastAPI to discover and register the route.

# summary and description define the happy path visible in Swagger UI.
# Failure paths (409, 422, 500) are handled globally by the exception handlers
# registered in app/__init__.py and documented via the ErrorResponse schema.
@auth_router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
    description=(
        "Creates a new user account with the provided email and password. "
        "The default ``user`` role is assigned automatically. "
        "Returns ``409`` if the email is already registered."
    )
)
async def register_route(body: RegisterRequest) -> None:
    await register(email=body.email, password=body.password)