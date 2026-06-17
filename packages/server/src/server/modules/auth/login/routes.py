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

# packages/server/src/server/modules/auth/login/routes.py
from datetime import datetime, timezone
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from postgres_lib import UserRepository
from auth_lib import auth_config, PasswordRepository, TokenRepository
from redis_lib import RefreshTokenRepository
from .schemas import LoginRequest, LoginResponse
from ..router import auth_router
from ....dependencies import get_async_db_session

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
        "token pair. Returns 401 if the email is not registered or the "
        "password is incorrect."
    ),
)
async def login_route(
    body: LoginRequest,
    db_session: AsyncSession = Depends(get_async_db_session),
) -> LoginResponse:
    """
    Authenticate a user and issue a new access/refresh token pair.

    Parameters
    ----------
    body : LoginRequest
        Request payload containing the email and plaintext password.
    db_session : AsyncSession
        Active async database session injected by get_async_db_session.

    Returns
    -------
    LoginResponse
        Access token and opaque refresh token for the authenticated user.

    Raises
    ------
    HTTPException
        401 Unauthorized if the email does not exist or the password is
        incorrect. A deliberately generic message is used to avoid leaking
        whether the email is registered.
    """
    user = await UserRepository.get_by_email(
        db_session,
        email=body.email,
        load_roles=True,
        load_permissions=True,
    )

    if user is None or not PasswordRepository.verify(body.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    permissions = list({
        perm.permission
        for role in user.roles
        for perm in role.permissions
    })

    now = datetime.now(timezone.utc)
    access_token = TokenRepository.create_access_token(
        user_id=user.id,
        permissions=permissions,
        now=now,
    )
    refresh_token = TokenRepository.create_refresh_token()

    await RefreshTokenRepository.save(
        token=refresh_token,
        user_id=user.id,
        ttl_seconds=auth_config.refresh_token_ttl,
    )

    await db_session.commit()

    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )