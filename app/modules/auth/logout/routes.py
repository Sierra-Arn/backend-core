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

# app/modules/auth/logout/routes.py
from fastapi import status
from .schemas import LogoutRequest
from .domen import logout
from ..router import auth_router


@auth_router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Terminate the current session",
    description=(
        "Blacklists the provided access token and deletes the refresh token "
        "from the database. Returns ``401`` if the access token is invalid "
        "or expired."
    ),
)
async def logout_route(body: LogoutRequest) -> None:
    await logout(
        access_token=body.access_token,
        refresh_token=body.refresh_token,
    )