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
    the BaseConfig precedence rules. Each logical concern — JWT blacklist,
    refresh tokens, and rate limiting — is isolated to its own Redis database,
    allowing independent flushing and monitoring.

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
    blacklist_db_index : int
        Redis database number used for JWT blacklist entries. Default is 0.
    refresh_token_db_index : int
        Redis database number used for opaque refresh token entries.
        Default is 1.
    rate_limit_db_index : int
        Redis database number used for rate limiting counters. Default is 2.
    blacklist_url : str
        Read-only property assembling the Redis connection URI for the
        JWT blacklist database.
    refresh_token_url : str
        Read-only property assembling the Redis connection URI for the
        refresh token database.
    rate_limit_url : str
        Read-only property assembling the Redis connection URI for the
        rate limiting database.
    """

    env_prefix: ClassVar[str] = "REDIS_"

    host: str = "127.0.0.1"
    port: int = Field(default=6379, ge=1, le=65535)
    user_name: str
    user_password: str
    blacklist_db_index: int = Field(default=0)
    refresh_token_db_index: int = Field(default=1)
    rate_limit_db_index: int = Field(default=2)

    def _build_url(self, db: int) -> str:
        """
        Assemble a Redis connection URI for the given database index.

        Parameters
        ----------
        db : int
            Redis database number to include as the URI path component.

        Returns
        -------
        str
            Complete Redis connection URI in the format
            redis://username:password@host:port/db.
        """
        return (
            f"redis://{self.user_name}:"
            f"{self.user_password}@"
            f"{self.host}:{self.port}/"
            f"{db}"
        )

    @property
    def blacklist_url(self) -> str:
        """
        Build Redis connection URL for the JWT blacklist database.

        Returns
        -------
        str
            Redis URI pointing to blacklist_db_index.
        """
        return self._build_url(self.blacklist_db_index)

    @property
    def refresh_token_url(self) -> str:
        """
        Build Redis connection URL for the refresh token database.

        Returns
        -------
        str
            Redis URI pointing to refresh_token_db_index.
        """
        return self._build_url(self.refresh_token_db_index)

    @property
    def rate_limit_url(self) -> str:
        """
        Build Redis connection URL for rate limiting counters.

        Returns
        -------
        str
            Redis URI pointing to rate_limit_db_index.
        """
        return self._build_url(self.rate_limit_db_index)


redis_config = RedisConfig()