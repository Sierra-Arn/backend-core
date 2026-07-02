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

# packages/services/src/tokens_lib/services/access_token.py
import uuid
from datetime import datetime
import jwt
from redis_lib import blacklist_redis_client
from ..config import tokens_config


class AccessTokenService:
    """
    Stateless service for issuing, decoding, and revoking JWT access tokens.

    All methods are classmethods and operate purely on the arguments passed
    to them, with no shared mutable state. Token signing parameters are read
    from tokens_config. Revocation entries are stored in the dedicated
    blacklist Redis database.
    """

    @classmethod
    def create(
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
            defined in tokens_config.

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
            "exp": now.timestamp() + tokens_config.access_token_ttl,
        }
        return jwt.encode(
            payload,
            tokens_config.jwt_secret_key,
            algorithm=tokens_config.jwt_algorithm,
        )

    @classmethod
    def decode(cls, token: str) -> dict:
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
            tokens_config.jwt_secret_key,
            algorithms=[tokens_config.jwt_algorithm],
        )

    @classmethod
    async def revoke(
        cls,
        jti: str,
        ttl_seconds: int,
    ) -> None:
        """
        Add a token JTI to the blacklist with a limited lifetime.

        Parameters
        ----------
        jti : str
            Unique JWT ID extracted from the token payload.
        ttl_seconds : int
            Remaining lifetime of the token in seconds.

        Notes
        -----
        The TTL must be set to the token's remaining lifetime rather than
        its full original TTL. Setting a longer TTL wastes Redis memory by
        keeping entries alive after the token would have expired naturally
        and been rejected by exp validation anyway. Setting a shorter TTL
        creates a window where a revoked token could pass the blacklist
        check after the Redis key expires but before the token's exp is
        reached.
        """
        await blacklist_redis_client.setex(
            name=jti,
            time=ttl_seconds,
            value=1,
        )

    @classmethod
    async def is_revoked(cls, jti: str) -> bool:
        """
        Check whether a token JTI is present in the blacklist.

        Parameters
        ----------
        jti : str
            Unique JWT ID extracted from the token payload.

        Returns
        -------
        bool
            True if the token has been revoked and authentication should
            fail. False if the token is not blacklisted and may proceed
            to further validation.

        Notes
        -----
        This method is called on every authenticated request, making its
        performance critical. Redis EXISTS runs in O(1) time and typically
        completes in under 1ms on a low-latency connection, keeping the
        per-request overhead negligible.

        EXISTS for a single key always returns either 0 or 1, never more,
        because Redis keys are unique by definition. A repeated SETEX with
        the same key simply overwrites the existing entry rather than
        creating a duplicate.
        """
        return await blacklist_redis_client.exists(jti) == 1