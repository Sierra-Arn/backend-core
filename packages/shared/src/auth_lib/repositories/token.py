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

# packages/shared/src/auth_lib/repositories/token.py
import uuid
import secrets
from datetime import datetime
import jwt
from ..config import auth_config


class TokenRepository:
    """
    Stateless repository for issuing and validating authentication tokens.

    All methods are classmethods that operate on the shared auth configuration
    directly, keeping the repository stateless and avoiding any shared mutable
    state. Covers the full token lifecycle: access token issuance, access token
    validation, and refresh token generation.
    """

    @classmethod
    def create_access_token(
        cls,
        user_id: int,
        permissions: list[str],
        now: datetime,
    ) -> str:
        """
        Issue a signed JWT access token for the given user.

        Parameters
        ----------
        user_id : int
            Primary key of the authenticated user. Stored in the sub claim
            as a string per the JWT specification.
        permissions : list[str]
            Permission strings assigned to the user across all their roles.
            Embedded directly in the payload so that authorization checks
            do not require an additional database round-trip.
        now : datetime
            Current UTC timestamp passed in by the caller. Shared with
            refresh token creation so that both tokens are issued against
            the same reference point in time.

        Returns
        -------
        str
            Signed JWT string encoded with the algorithm and secret key
            defined in auth_config.

        Notes
        -----
        The payload contains the following claims.

        sub is the subject — the user's primary key serialized as a string.
        The JWT specification requires sub to be a string value, so the
        integer user_id is converted via str() before encoding. Callers
        that need the numeric ID must cast back with int(payload["sub"]).

        jti is a random UUID4 string that uniquely identifies this token
        instance. Used as the Redis key when the token is added to the
        blacklist on logout.

        permissions is a flat list of permission strings assigned to the
        user at the time of issuance, collected across all their roles.
        Permissions are embedded at login and are not updated automatically
        if role or permission assignments change — the user must
        re-authenticate to receive a token reflecting the latest state.

        exp is the expiry timestamp in UTC, set to now plus access_token_ttl
        seconds. Passed as a Unix timestamp float to avoid timezone-awareness
        issues across PyJWT versions. PyJWT validates this claim automatically
        on decode and raises jwt.ExpiredSignatureError if the token has elapsed.
        """
        payload = {
            "sub": str(user_id),
            "jti": str(uuid.uuid4()),
            "permissions": permissions,
            "exp": now.timestamp() + auth_config.access_token_ttl,
        }
        return jwt.encode(
            payload,
            auth_config.jwt_secret_key,
            algorithm=auth_config.jwt_algorithm,
        )

    @classmethod
    def decode_access_token(cls, token: str) -> dict:
        """
        Decode and validate a JWT access token.

        Parameters
        ----------
        token : str
            Raw JWT string to decode and validate.

        Returns
        -------
        dict
            Decoded payload containing all claims: sub, jti, permissions,
            and exp.

        Raises
        ------
        jwt.ExpiredSignatureError
            If the token's exp claim is in the past.
        jwt.InvalidTokenError
            If the token signature is invalid, the token is malformed,
            or any other validation check fails.

        Notes
        -----
        PyJWT validates the exp claim automatically during decoding.
        No manual timestamp comparison is required after this call returns.
        """
        return jwt.decode(
            token,
            auth_config.jwt_secret_key,
            algorithms=[auth_config.jwt_algorithm],
        )

    @classmethod
    def create_refresh_token(cls) -> str:
        """
        Generate a cryptographically secure opaque refresh token.

        Uses secrets.token_urlsafe with the byte length defined by
        auth_config.refresh_token_length, producing a URL-safe
        base64-encoded string that fits within the String(512) column
        constraint in the database.

        Returns
        -------
        str
            URL-safe base64-encoded random string to be stored in Redis
            and returned to the client. Never decoded or interpreted by
            the server — looked up by exact match only on every refresh
            request.
        """
        return secrets.token_urlsafe(auth_config.refresh_token_length)