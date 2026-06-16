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

# app/modules/account/change_password/routes.py
from fastapi import Depends, status
from .schemas import ChangePasswordRequest
from .domen import change_password
from ..router import account_router
from ....shared.auth import get_current_user


@account_router.patch(
    "/change-password",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Change the authenticated user's password",
    description=(
        "Verifies the current password and replaces it with the new one. "
        "Invalidates the current session by blacklisting the access token "
        "and deleting the refresh token. Returns ``401`` if the current "
        "password is incorrect. "
        "The target user is identified by the ``sub`` claim of the Bearer token — "
        "a user can only change their own password."
    ),
)
async def change_password_route(
    body: ChangePasswordRequest,
    payload: dict = Depends(get_current_user),
) -> None:
    await change_password(
        user_id=int(payload["sub"]),
        current_password=body.password,
        new_password=body.new_password,
        refresh_token=body.refresh_token,
        access_token_jti=payload["jti"],
        access_token_exp=payload["exp"],
    )