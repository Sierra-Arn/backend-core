# app/shared/redis/db/rate_limit.py

"""
Without rate limiting, a single client can send an unbounded number of
requests in a short period — exhausting server resources, degrading
response times for legitimate users, or brute-forcing sensitive endpoints
such as login or password reset.

Rate limiting enforces a maximum request count per client within a rolling
time window, after which further requests are rejected with ``429 Too Many
Requests`` until the window advances.

Redis is chosen over SQL for this purpose for the same reasons as the JWT
blacklist — native TTL support for automatic key cleanup and sub-millisecond
read/write performance that keeps per-request overhead negligible.

**Sliding window** is used instead of the simpler fixed window algorithm
because fixed windows have a boundary vulnerability: a client can send the
full quota at the very end of one window and again at the very start of the
next, effectively doubling the allowed burst. The sliding window evaluates
the last ``window_seconds`` seconds relative to *now*, so the allowed rate
is enforced continuously with no exploitable boundary.

Each request is stored as a member of a Redis sorted set with the current
Unix timestamp as its score. On every check, entries older than the window
are evicted via ``ZREMRANGEBYSCORE`` before counting, ensuring the set
always reflects only the requests within the active window.
"""

import time
import uuid
import redis.asyncio as aioredis
from .config import redis_config


def _make_key(ip: str) -> str:
    """
    Build a namespaced Redis key for a given IP address.

    Parameters
    ----------
    ip : str
        Client IP address.

    Returns
    -------
    str
        Redis key in the format ``<rate_limit_prefix>:<ip>``.
    """
    return f"{redis_config.rate_limit_prefix}:{ip}"


async def is_allowed(client: aioredis.Redis, ip: str) -> bool:
    """
    Check whether a client IP is within the allowed request rate and record
    the current request if so.

    If the request is allowed, a new entry is added to the sorted set
    and the key's TTL is refreshed to ``rate_limit_window_seconds`` to enable
    automatic cleanup of idle keys.

    Parameters
    ----------
    client : redis.asyncio.Redis
        Redis client to use for the operation.
    ip : str
        Client IP address (e.g., ``"192.168.1.1"``).

    Returns
    -------
    bool
        ``True`` if the request is within the allowed rate and has been
        recorded. ``False`` if the limit has been reached and the request
        should be rejected.

    Notes
    -----
    The sliding window is implemented as follows:

    1. ``ZREMRANGEBYSCORE`` removes all entries with a timestamp older
        than ``now - window_seconds``, keeping only requests within the
        current window.
    2. ``ZCARD`` returns the number of remaining entries, i.e. the current
        request count within the window.
    3. If the count is below ``max_requests``, a new entry is added via
        ``ZADD`` using the current timestamp as the score and a random UUID
        as the member (to allow multiple requests at the same timestamp).
    4. ``EXPIRE`` resets the key TTL so that idle keys are eventually
        removed from Redis automatically.

    All four commands are executed in a single pipeline to minimize
    round-trips and keep the check-then-write sequence as atomic as possible.
    Note that this pipeline is not fully atomic — for strict atomicity
    under high concurrency a Lua script would be required. For most
    practical use cases this implementation is sufficient.
    """

    key = _make_key(ip)
    now = time.time()
    window_start = now - redis_config.rate_limit_window_seconds

    async with client.pipeline(transaction=False) as pipe:
        pipe.zremrangebyscore(key, "-inf", window_start)
        pipe.zcard(key)
        results = await pipe.execute()

    if results[1] >= redis_config.rate_limit_max_requests:
        return False

    async with client.pipeline(transaction=False) as pipe:
        pipe.zadd(key, {str(uuid.uuid4()): now})
        pipe.expire(key, redis_config.rate_limit_window_seconds)
        await pipe.execute()

    return True