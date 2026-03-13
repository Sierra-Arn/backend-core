# app/shared/auth/token.py
from datetime import datetime
import uuid
import secrets
import jwt
from .config import authentication_config


def create_access_token(user_id: int, permissions: list[str], now: datetime) -> str:
    """
    Issue a signed JWT access token for the given user.
 
    Parameters
    ----------
    user_id : int
        Primary key of the authenticated user.
        Stored in the ``sub`` claim as a string per the JWT specification.
    permissions : list[str]
        Permission strings assigned to the user across all their roles
        (e.g. ``["users:get", "users:delete"]``).
        Embedded directly in the payload so that authorization checks
        do not require an additional database round-trip.
    now : datetime
        Current UTC timestamp passed in by the caller.
        Shared with refresh token creation so that both tokens are issued
        against the same reference point in time.
 
    Returns
    -------
    str
        A signed JWT string encoded with the algorithm and secret key
        defined in ``authentication_config``.
 
    Notes
    -----
    The payload contains the following claims:
 
    ``sub``
        Subject — the user's primary key serialized as a string.
        The JWT specification requires ``sub`` to be a string value,
        so the integer ``user_id`` is converted via ``str()`` before encoding.
        Callers that need the numeric ID must cast back with ``int(payload["sub"])``.
    ``jti``
        JWT ID — a random UUID4 string that uniquely identifies this token
        instance. Used as the Redis key when the token is added to the
        blacklist on logout. Stored as a string to remain compatible with
        ``redis.setex``, which requires a string key.
    ``permissions``
        Flat list of permission strings assigned to the user at the time
        of issuance, collected across all their roles. Permissions are
        embedded at login and are not updated automatically if role or
        permission assignments change — the user must re-authenticate to
        receive a token reflecting the latest state.
    ``exp``
        Expiry timestamp in UTC, set to ``now + access_token_ttl`` seconds.
        Passed as a Unix timestamp float rather than a ``datetime`` object
        to avoid timezone-awareness issues across PyJWT versions.
        PyJWT validates this claim automatically on decode and raises
        ``jwt.ExpiredSignatureError`` if the token is past its expiry.
    """
    
    payload = {
        "sub": str(user_id),
        "jti": str(uuid.uuid4()),
        "permissions": permissions,
        "exp": now.timestamp() + authentication_config.access_token_ttl,
    }
    return jwt.encode(
        payload,
        authentication_config.jwt_secret_key,
        algorithm=authentication_config.jwt_algorithm,
    )


def decode_access_token(token: str) -> dict:
    """
    Decode and validate a JWT access token.

    Parameters
    ----------
    token : str
        The raw JWT string to decode and validate.

    Returns
    -------
    dict
        The decoded payload containing all claims (``sub``, ``jti``,
        ``roles``, ``exp``).

    Raises
    ------
    jwt.ExpiredSignatureError
        If the token's ``exp`` claim is in the past.
    jwt.InvalidTokenError
        If the token signature is invalid, the token is malformed,
        or any other validation check fails.

    Notes
    -----
    PyJWT validates the ``exp`` claim automatically during decoding.
    No manual timestamp comparison is required after this call returns.
    """

    return jwt.decode(
        token,
        authentication_config.jwt_secret_key,
        algorithms=[authentication_config.jwt_algorithm],
    )


def create_refresh_token() -> str:
    """
    Generate a cryptographically secure opaque refresh token.

    Uses ``secrets.token_urlsafe`` with the byte length defined by
    ``authentication_config.refresh_token_length``, producing a URL-safe
    base64-encoded string that fits within the ``String(512)`` column
    constraint of the ``refresh_tokens.token`` database column.

    Returns
    -------
    str
        A URL-safe base64-encoded random string to be stored as-is in the
        database and returned to the client. Never decoded or interpreted
        by the server — looked up by exact match only on every refresh request.
    """

    return secrets.token_urlsafe(authentication_config.refresh_token_length)