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

# app/modules/auth/login/routes.py
from fastapi import status
from .schemas import LoginRequest, LoginResponse
from .domen import login
from ..router import auth_router


# response_model tells FastAPI to use LoginResponse as the documented output
# schema for this endpoint — Swagger UI will render it as the expected response
# body under the 200 status code.
@auth_router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    response_model=LoginResponse,
    summary="Authenticate a user",
    description=(
        "Verifies the provided credentials and issues a new access/refresh "
        "token pair. Returns ``401`` if the email is not registered or the "
        "password is incorrect."
    ),
)
async def login_route(body: LoginRequest) -> LoginResponse:
    tokens = await login(email=body.email, password=body.password)
    return LoginResponse(**tokens)