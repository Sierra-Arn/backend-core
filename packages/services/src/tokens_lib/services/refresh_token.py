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

# packages/services/src/tokens_lib/services/refresh_token.py
import secrets
from redis_lib import refresh_token_redis_client
from ..config import tokens_config


class RefreshTokenService:
    """
    Stateless service for generating, persisting, and revoking opaque refresh
    tokens stored in Redis.

    All methods are classmethods and operate purely on the arguments passed
    to them, with no shared mutable state. Token generation parameters are
    read from tokens_config. Entries are stored in the dedicated refresh
    token Redis database and expire automatically after their configured TTL.
    """

    @classmethod
    def create(cls) -> str:
        """
        Generate a cryptographically secure opaque refresh token.

        Uses secrets.token_urlsafe with the byte length defined by
        tokens_config.refresh_token_length, producing a URL-safe
        base64-encoded string.

        Returns
        -------
        str
            URL-safe base64-encoded random string to be stored in Redis
            and returned to the client. Never decoded or interpreted by
            the server — looked up by exact match only on every refresh
            request.
        """
        return secrets.token_urlsafe(tokens_config.refresh_token_length)

    @classmethod
    async def save(
        cls,
        token: str,
        user_id: int,
    ) -> None:
        """
        Persist a refresh token entry mapped to the owning user.

        Parameters
        ----------
        token : str
            Opaque refresh token value issued to the client.
        user_id : int
            Primary key of the user who owns this token.
        """
        await refresh_token_redis_client.setex(
            name=token,
            time=tokens_config.refresh_token_ttl,
            value=user_id,
        )

    @classmethod
    async def get_user_id(cls, token: str) -> int | None:
        """
        Retrieve the user_id associated with a refresh token.

        Parameters
        ----------
        token : str
            Opaque refresh token value to look up.

        Returns
        -------
        int or None
            Primary key of the owning user if the token exists and has
            not expired. None if the token is not found or has elapsed.
        """
        value = await refresh_token_redis_client.get(token)
        return int(value) if value is not None else None

    @classmethod
    async def revoke(cls, token: str) -> bool:
        """
        Delete a refresh token entry, immediately invalidating it.

        Parameters
        ----------
        token : str
            Opaque refresh token value to revoke.

        Returns
        -------
        bool
            True if the token was found and deleted. False if the token
            did not exist or had already expired.
        """
        return await refresh_token_redis_client.delete(token) == 1

    @classmethod
    async def exists(cls, token: str) -> bool:
        """
        Check whether a refresh token entry is present in Redis.

        Parameters
        ----------
        token : str
            Opaque refresh token value to check.

        Returns
        -------
        bool
            True if the token exists and has not expired. False otherwise.

        Notes
        -----
        This method is an O(1) Redis EXISTS check and completes in under
        1ms on a low-latency connection. It can be used before get_user_id
        when the caller only needs to verify token presence without
        retrieving the associated user_id.
        """
        return await refresh_token_redis_client.exists(token) == 1