# app/shared/auth/dependencies.py
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from .token import decode_access_token
from ..redis.db import async_redis_client, is_revoked


_bearer_scheme = HTTPBearer()
"""
FastAPI security scheme that extracts the Bearer token from the
``Authorization`` header and rejects requests that omit it with ``403``.
"""


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
) -> dict:
    """
    Validate the Bearer token and return the decoded payload.

    Performs three checks in order:

    1. Decodes and verifies the JWT signature and expiry.
    2. Checks that the token's ``jti`` has not been blacklisted in Redis
       (i.e., the user has not logged out since this token was issued).
    3. Returns the payload so that downstream dependencies and route
       handlers can read ``sub`` (user ID) and ``permissions`` without an
       additional database round-trip.

    Parameters
    ----------
    credentials : HTTPAuthorizationCredentials
        Bearer token extracted from the ``Authorization`` header by
        FastAPI's ``HTTPBearer`` scheme.

    Returns
    -------
    dict
        Decoded JWT payload containing ``sub``, ``jti``, ``permissions``,
        and ``exp``.

    Raises
    ------
    HTTPException
        ``401 Unauthorized`` if the token is expired, has an invalid
        signature, is malformed, or has been blacklisted.
    """

    token = credentials.credentials

    try:
        payload = decode_access_token(token)
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

    if await is_revoked(client=async_redis_client, jti=payload["jti"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token has been revoked.",
        )

    return payload


def require_permission(permission: str):
    """
    Return a dependency that ensures the current user has the required permission.

    Intended to be used with ``Depends`` on individual routes or routers
    that should be restricted to a specific permission.

    Parameters
    ----------
    permission : str
        The permission string the user must have.

    Returns
    -------
    callable
        A FastAPI dependency function that resolves to the decoded JWT
        payload if the permission check passes.

    Raises
    ------
    HTTPException
        ``403 Forbidden`` if the current user does not have the required
        permission.
    """
    
    async def _require_permission(payload: dict = Depends(get_current_user)) -> dict:
        if permission not in payload.get("permissions", []):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied.",
            )
        return payload

    return _require_permission