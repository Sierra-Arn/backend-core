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

# packages/shared/src/redis_lib/repositories/jwt_blacklist.py
from ..client import async_redis_client
from ..config import redis_config


class JwtBlacklistRepository:
    """
    Stateless repository for managing revoked JWT entries in Redis.

    All methods are classmethods that operate on the shared async Redis
    client directly, keeping the repository stateless and avoiding any
    shared mutable state. The blacklist maps jti values to a placeholder
    that signals revocation; the actual value stored is irrelevant —
    only key presence is checked.
    """

    @classmethod
    def _make_key(cls, jti: str) -> str:
        """
        Build a namespaced Redis key for a given JTI.

        Parameters
        ----------
        jti : str
            Unique JWT ID extracted from the token payload.

        Returns
        -------
        str
            Redis key in the format blacklist_prefix:jti.
        """
        return f"{redis_config.blacklist_prefix}:{jti}"

    @classmethod
    async def add(
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
        await async_redis_client.setex(
            name=cls._make_key(jti),
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
        return await async_redis_client.exists(cls._make_key(jti)) == 1