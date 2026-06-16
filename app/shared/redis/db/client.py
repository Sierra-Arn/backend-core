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