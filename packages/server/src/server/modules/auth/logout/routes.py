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

# packages/server/src/server/modules/auth/logout/routes.py
from datetime import datetime, timezone
from fastapi import Depends, status
from redis_lib import JwtBlacklistRepository, RefreshTokenRepository
from .schemas import LogoutRequest
from ..router import auth_router
from ....dependencies import get_current_user


@auth_router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Terminate the current session",
    description=(
        "Blacklists the current access token and revokes the refresh token "
        "in Redis. Returns 401 if the access token is invalid or expired."
    ),
)
async def logout_route(
    body: LogoutRequest,
    payload: dict = Depends(get_current_user),
) -> None:
    """
    Invalidate the current session by blacklisting the access token and
    revoking the refresh token in Redis.

    Parameters
    ----------
    body : LogoutRequest
        Request payload containing the opaque refresh token to revoke.
    payload : dict
        Decoded JWT payload injected by get_current_user. Provides jti
        and exp claims needed to blacklist the access token.

    Notes
    -----
    The access token is blacklisted only if its remaining TTL is positive.
    A token that has already expired is rejected by get_current_user before
    this handler is reached, so a zero or negative TTL here would indicate
    a clock skew edge case and is safe to skip.
    """
    jti = payload["jti"]
    exp = payload["exp"]
    ttl = int(exp - datetime.now(timezone.utc).timestamp())

    if ttl > 0:
        await JwtBlacklistRepository.add(jti=jti, ttl_seconds=ttl)

    await RefreshTokenRepository.revoke(token=body.refresh_token)