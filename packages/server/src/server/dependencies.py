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

# packages/server/src/server/dependencies.py
from typing import AsyncGenerator
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from postgres_lib import async_session_factory
from auth_lib import TokenRepository
from redis_lib import JwtBlacklistRepository


async def get_async_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Manage the lifecycle of an async database session for a single request.

    Opens a new async session, yields it for ORM operations, and guarantees
    cleanup with automatic rollback on failure. Committing is the caller's
    responsibility: a write that is not explicitly committed before the context
    exits is discarded when the session closes. On any exception the session is
    rolled back and the exception re-raised.

    Yields
    ------
    AsyncSession
        Active async session bound to the async engine.
    """
    async with async_session_factory() as db:
        try:
            yield db
        except Exception:
            await db.rollback()
            raise


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
) -> dict:
    """
    Validate the Bearer token and return the decoded payload.

    Performs three checks in order: decodes and verifies the JWT signature
    and expiry; checks that the token's jti has not been blacklisted in
    Redis meaning the user has not logged out since the token was issued;
    returns the payload so that downstream dependencies and route handlers
    can read sub and permissions without an additional database round-trip.

    Parameters
    ----------
    credentials : HTTPAuthorizationCredentials
        Bearer token extracted from the Authorization header by FastAPI's
        HTTPBearer scheme.

    Returns
    -------
    dict
        Decoded JWT payload containing sub, jti, permissions, and exp.

    Raises
    ------
    HTTPException
        401 Unauthorized if the token is expired, has an invalid signature,
        is malformed, or has been blacklisted.
    """
    token = credentials.credentials

    try:
        payload = TokenRepository.decode_access_token(token)
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token has expired.",
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token.",
        )

    if await JwtBlacklistRepository.is_revoked(jti=payload["jti"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token has been revoked.",
        )

    return payload


def require_permission(permission: str):
    """
    Return a dependency that ensures the current user holds the required permission.

    Intended to be used with Depends on individual routes or routers that
    should be restricted to a specific permission.

    Parameters
    ----------
    permission : str
        Permission string the user must have in their token payload.

    Returns
    -------
    callable
        FastAPI dependency function that resolves to the decoded JWT payload
        if the permission check passes.

    Raises
    ------
    HTTPException
        403 Forbidden if the current user does not hold the required permission.
    """
    async def _require_permission(
        payload: dict = Depends(get_current_user),
    ) -> dict:
        if permission not in payload.get("permissions", []):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied.",
            )
        return payload

    return _require_permission