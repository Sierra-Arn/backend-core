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

# packages/server/src/server/modules/auth/refresh/routes.py
from datetime import datetime, timezone
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from postgres_lib import UserRepository
from auth_lib import TokenRepository
from redis_lib import RefreshTokenRepository
from .schemas import RefreshRequest, RefreshResponse
from ..router import auth_router
from ....dependencies import get_async_db_session


@auth_router.post(
    "/refresh",
    status_code=status.HTTP_200_OK,
    response_model=RefreshResponse,
    summary="Reissue an access token",
    description=(
        "Validates the provided refresh token and issues a new access token. "
        "The refresh token itself is not rotated and remains valid until its "
        "original expiry. Returns 401 if the refresh token does not exist or "
        "has expired."
    ),
)
async def refresh_route(
    body: RefreshRequest,
    db_session: AsyncSession = Depends(get_async_db_session),
) -> RefreshResponse:
    """
    Issue a new access token for the owner of the provided refresh token.

    The refresh token is validated against Redis and remains unchanged after
    this call. Only the access token is reissued, preserving the original
    refresh token lifetime regardless of how many times this endpoint is called.

    Parameters
    ----------
    body : RefreshRequest
        Request payload containing the opaque refresh token.
    db_session : AsyncSession
        Active async database session injected by get_async_db_session.
        Used to load the user and their roles for access token issuance.

    Returns
    -------
    RefreshResponse
        Newly issued access token.

    Raises
    ------
    HTTPException
        401 Unauthorized if the refresh token does not exist or has expired.
    """
    user_id = await RefreshTokenRepository.get_user_id(token=body.refresh_token)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token.",
        )

    user = await UserRepository.get_by_id(
        db_session,
        obj_id=user_id,
        load_roles=True,
        load_permissions=True,
    )

    permissions = list({
        perm.permission
        for role in user.roles
        for perm in role.permissions
    })

    access_token = TokenRepository.create_access_token(
        user_id=user.id,
        permissions=permissions,
        now=datetime.now(timezone.utc),
    )

    return RefreshResponse(access_token=access_token)