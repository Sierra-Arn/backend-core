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

# packages/shared/src/redis_lib/repositories/rate_limit.py
import time
import uuid
from ..client import async_redis_client
from ..config import redis_config


class RateLimitRepository:
    """
    Stateless repository for managing sliding window rate limit entries in Redis.

    All methods are classmethods that operate on the shared async Redis
    client directly, keeping the repository stateless and avoiding any
    shared mutable state. The sliding window is implemented as a Redis
    sorted set where each member is a unique request identifier and each
    score is the request timestamp.
    """

    @classmethod
    def _make_key(cls, ip: str) -> str:
        """
        Build a namespaced Redis key for a given IP address.

        Parameters
        ----------
        ip : str
            Client IP address.

        Returns
        -------
        str
            Redis key in the format rate_limit_prefix:ip.
        """
        return f"{redis_config.rate_limit_prefix}:{ip}"

    @classmethod
    async def is_allowed(cls, ip: str) -> bool:
        """
        Check whether a client IP is within the allowed request rate and
        record the current request if so.

        Parameters
        ----------
        ip : str
            Client IP address to check and record.

        Returns
        -------
        bool
            True if the request is within the allowed rate and has been
            recorded. False if the limit has been reached and the request
            should be rejected.

        Notes
        -----
        The sliding window is implemented using a Redis sorted set in two
        sequential pipelines.

        The first pipeline removes stale entries and reads the current count:
        ZREMRANGEBYSCORE drops all members with a timestamp older than
        now minus window_seconds, keeping only requests within the active
        window; ZCARD then returns the number of remaining members, which
        represents the current request count.

        If the count is below max_requests, the second pipeline records the
        request and resets the TTL: ZADD inserts the current timestamp as
        the score with a random UUID as the member to allow multiple requests
        at identical timestamps; EXPIRE resets the key lifetime to
        window_seconds so that idle keys are eventually removed automatically.

        Both pipelines use transaction=False because the commands within each
        pipeline are independent and do not require MULTI/EXEC semantics.
        This implementation is not fully atomic across both pipelines — under
        extreme concurrency a small number of requests may slip through near
        the limit boundary. For strict atomicity a Lua script would be
        required. For most practical rate limiting use cases this is
        sufficient.
        """
        key = cls._make_key(ip)
        now = time.time()
        window_start = now - redis_config.rate_limit_window_seconds

        async with async_redis_client.pipeline(transaction=False) as pipe:
            pipe.zremrangebyscore(key, "-inf", window_start)
            pipe.zcard(key)
            results = await pipe.execute()

        if results[1] >= redis_config.rate_limit_max_requests:
            return False

        async with async_redis_client.pipeline(transaction=False) as pipe:
            pipe.zadd(key, {str(uuid.uuid4()): now})
            pipe.expire(key, redis_config.rate_limit_window_seconds)
            await pipe.execute()

        return True