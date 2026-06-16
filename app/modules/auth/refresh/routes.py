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

# app/modules/auth/refresh/routes.py
from fastapi import status
from .schemas import RefreshRequest, RefreshResponse
from .domen import refresh
from ..router import auth_router


@auth_router.post(
    "/refresh",
    status_code=status.HTTP_200_OK,
    response_model=RefreshResponse,
    summary="Rotate the token pair",
    description=(
        "Validates the provided refresh token, issues a new access/refresh "
        "token pair, and invalidates the old refresh token. Returns ``401`` "
        "if the refresh token does not exist or has expired."
    ),
)
async def refresh_route(body: RefreshRequest) -> RefreshResponse:
    tokens = await refresh(refresh_token=body.refresh_token)
    return RefreshResponse(**tokens)