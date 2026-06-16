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

# app/shared/redis/db/config.py
from typing import ClassVar
from urllib.parse import quote_plus
from pydantic import Field
from ...base_config import BaseConfig


class RedisConfig(BaseConfig):
    """
    Configuration schema for Redis service.

    Attributes
    ----------
    host : str
        Hostname or IP address of the Redis server. Default is `"127.0.0.1"`.
    external_port : int
        TCP port the server listens on. Must be in the range 1-65535.
        Default is `6379`.
    user_name : str
        Username for Redis authentication.
    user_password : str
        Password for Redis authentication.
    db_index : int
        Redis database number to connect to. Default is `0`.
    blacklist_prefix : str
        Key prefix for JWT blacklist entries. Default is `"blacklist"`.
    rate_limit_prefix : str
        Key prefix for rate limiting entries. Default is `"rl"`.
    rate_limit_max_requests : int
        Maximum number of requests a single IP address may send within
        one rate limit window. Default is `100`.
    rate_limit_window_seconds : int
        Duration of the sliding rate limit window in seconds. Default is `60`.

    Notes
    -----
    This class inherits from `app.shared.base_config.BaseConfig`.
    For details on configuration loading behavior, see its documentation.
    """

    env_prefix: ClassVar[str] = "REDIS_"

    host: str = "127.0.0.1"
    external_port: int = Field(default=6379, ge=1, le=65535)
    user_name: str
    user_password: str
    db_index: int = Field(default=0)
    blacklist_prefix: str = "blacklist"
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
            Complete Redis connection URL with URL-encoded credentials
            in the format: redis://username:password@host:port

        Notes
        -----
        The password is URL-encoded using `quote_plus` to safely handle
        special characters that might be present in the password string.
        """
        
        return (
            f"redis://{self.user_name}:"
            f"{quote_plus(self.user_password)}@"
            f"{self.host}:{self.external_port}"
        )


# Initialize Redis configuration singleton.
# Since Redis server settings are static for the application's lifetime
# and any configuration changes require a full application restart,
# it is safe to instantiate the config once at module level and reuse
# it throughout the application as a singleton.
redis_config = RedisConfig()