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

# app/shared/redis/repositories/jwt_blacklist.py

"""
JWT access tokens are stateless by design — once issued, they remain
cryptographically valid until their ``exp`` claim is reached. This means
that simply deleting a token on the client side (e.g., on logout) does not
prevent someone who captured the token from continuing to use it.

The blacklist solves this by storing the ``jti`` (JWT ID) of every revoked
token in Redis. On each authentication check, the caller verifies whether
the incoming token's ``jti`` is present in the blacklist. If it is,
authentication fails — regardless of the token's ``exp``.

Redis is chosen over SQL for this purpose for two reasons:

1. **Native TTL support.** Each blacklist entry is stored with a TTL equal
   to the token's remaining lifetime. Redis automatically removes expired
   entries, so the blacklist never grows unboundedly and requires no
   scheduled cleanup jobs.

2. **O(1) read performance.** Blacklist lookups happen on every
   authentication check. Redis ``EXISTS`` completes in sub-millisecond
   time, making the overhead negligible compared to a SQL ``SELECT``
   with index traversal.
"""

import redis.asyncio as aioredis
from .config import redis_config


def _make_key(jti: str) -> str:
    """
    Build a namespaced Redis key for a given JTI.

    Parameters
    ----------
    jti : str
        Unique JWT ID extracted from the token payload (``payload["jti"]``).

    Returns
    -------
    str
        Redis key in the format ``<blacklist_prefix>:<jti>``.
    """

    return f"{redis_config.blacklist_prefix}:{jti}"


async def add_to_blacklist(client: aioredis.Redis, jti: str, ttl_seconds: int) -> None:
    """
    Add a token JTI to the blacklist with a limited lifetime.

    Parameters
    ----------
    client : redis.asyncio.Redis
        Redis client to use for the operation.
    jti : str
        Unique JWT ID extracted from the token payload (``payload["jti"]``).
    ttl_seconds : int
        Remaining lifetime of the token in seconds.

    Notes
    -----
    The TTL should be set to the token's *remaining* lifetime rather than
    its full original TTL. Setting a longer TTL wastes Redis memory by
    keeping entries alive after the token would have expired naturally and
    been rejected anyway. Setting a shorter TTL creates a window where a
    revoked token could pass the blacklist check after the Redis key is
    gone but before the token's ``exp`` is reached.
    """

    await client.setex(name=_make_key(jti), time=ttl_seconds, value=1)


async def is_revoked(client: aioredis.Redis, jti: str) -> bool:
    """
    Check whether a token JTI is present in the blacklist.

    Parameters
    ----------
    client : redis.asyncio.Redis
        Redis client to use for the operation.
    jti : str
        Unique JWT ID extracted from the token payload (``payload["jti"]``).

    Returns
    -------
    bool
        ``True`` if the token has been revoked and authentication should
        fail. ``False`` if the token is not blacklisted and may proceed
        to further validation.

    Notes
    -----
    This function is called on every authentication check, making its
    performance critical. Redis ``EXISTS`` runs in O(1) time and typically
    completes in under 1ms on a local or low-latency connection, which
    keeps the per-check overhead negligible.

    Comparing against ``1`` is safe because Redis is a key-value store where
    keys are unique by definition — a duplicate ``jti`` entry is impossible.
    A repeated ``SETEX`` with the same key simply overwrites the existing one.
    Therefore, ``EXISTS`` for a single key always returns either ``0`` or ``1``,
    never more.
    """

    return await client.exists(_make_key(jti)) == 1