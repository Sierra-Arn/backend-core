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

# packages/shared/src/redis_lib/repositories/refresh_token.py
from ..client import async_redis_client
from ..config import redis_config


class RefreshTokenRepository:
    """
    Stateless repository for managing opaque refresh token entries in Redis.

    All methods are classmethods that operate on the shared async Redis
    client directly, keeping the repository stateless and avoiding any
    shared mutable state. Each entry maps an opaque token value to the
    owning user_id and expires automatically after the token lifetime
    elapses, eliminating the need for explicit cleanup queries.
    """

    @classmethod
    def _make_key(cls, token: str) -> str:
        """
        Build a namespaced Redis key for a given refresh token value.

        Parameters
        ----------
        token : str
            Opaque refresh token value issued to the client.

        Returns
        -------
        str
            Redis key in the format refresh_token_prefix:token_value.
        """
        return f"{redis_config.refresh_token_prefix}:{token}"

    @classmethod
    async def save(
        cls,
        token: str,
        user_id: int,
        ttl_seconds: int,
    ) -> None:
        """
        Persist a refresh token entry mapped to the owning user.

        Parameters
        ----------
        token : str
            Opaque refresh token value issued to the client.
        user_id : int
            Primary key of the user who owns this token.
        ttl_seconds : int
            Lifetime of the token in seconds. The Redis key expires
            automatically after this duration, revoking the token
            without requiring an explicit delete.
        """
        await async_redis_client.setex(
            name=cls._make_key(token),
            time=ttl_seconds,
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
        value = await async_redis_client.get(cls._make_key(token))
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
        return await async_redis_client.delete(cls._make_key(token)) == 1

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
        return await async_redis_client.exists(cls._make_key(token)) == 1
