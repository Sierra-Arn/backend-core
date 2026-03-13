# app/shared/redis/db/client.py
import redis.asyncio as aioredis
from .config import redis_config


async_redis_client = aioredis.from_url(
    redis_config.connection_url,
    db=redis_config.db_index,
    decode_responses=True,
)
"""
Asynchronous Redis client configured via application settings.
"""