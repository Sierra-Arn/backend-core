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

# packages/shared/src/redis_lib/config.py
from typing import ClassVar
from pydantic import Field
from base_lib import BaseConfig


class RedisConfig(BaseConfig):
    """
    Configuration schema for Redis service connectivity.

    Stores connection parameters for accessing a Redis instance. All fields
    support resolution from environment variables prefixed with REDIS_ following
    the BaseConfig precedence rules. The connection_url property assembles a
    complete Redis URI from the configured credentials and endpoint.

    Attributes
    ----------
    host : str
        Hostname or IP address of the Redis server endpoint.
        Default is "127.0.0.1".
    port : int
        TCP port for the Redis service; validated to lie within the standard
        16-bit range. Default is 6379.
    user_name : str
        Username for Redis ACL-based authentication.
    user_password : str
        Password for Redis authentication; treated as sensitive data.
    db_index : int
        Redis database number to connect to. Default is 0.
    blacklist_prefix : str
        Key prefix for JWT blacklist entries. Keys are structured as
        blacklist_prefix:jti and map to the remaining TTL of the token.
        Default is "blacklist".
    refresh_token_prefix : str
        Key prefix for opaque refresh token entries. Keys are structured
        as refresh_token_prefix:token_value and map to the owning user_id.
        Default is "refresh_token".
    rate_limit_prefix : str
        Key prefix for rate limiting entries. Keys are structured as
        rate_limit_prefix:ip_address and map to the request count within
        the current window. Default is "rl".
    rate_limit_max_requests : int
        Maximum number of requests a single IP address may send within
        one rate limit window. Default is 100.
    rate_limit_window_seconds : int
        Duration of the sliding rate limit window in seconds. Default is 60.
    connection_url : str
        Read-only property assembling the full Redis connection URI with
        credentials.
    """

    env_prefix: ClassVar[str] = "REDIS_"

    host: str = "127.0.0.1"
    port: int = Field(default=6379, ge=1, le=65535)
    user_name: str
    user_password: str
    db_index: int = Field(default=0)
    blacklist_prefix: str = "blacklist"
    refresh_token_prefix: str = "refresh_token"
    rate_limit_prefix: str = "rl"
    rate_limit_max_requests: int = Field(default=100, ge=1)
    rate_limit_window_seconds: int = Field(default=60, ge=1)

    @property
    def connection_url(self) -> str:
        """
        Build Redis connection URL from configuration settings.

        Returns
        -------
        str
            Complete Redis connection URI in the format
            redis://username:password@host:port
        """
        return (
            f"redis://{self.user_name}:"
            f"{self.user_password}@"
            f"{self.host}:{self.port}"
        )


redis_config = RedisConfig()