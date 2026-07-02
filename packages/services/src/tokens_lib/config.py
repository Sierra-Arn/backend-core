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

# packages/services/src/tokens_lib/config.py
from typing import ClassVar
from pydantic import Field
from base_lib import BaseConfig


class TokensConfig(BaseConfig):
    """
    Configuration schema for JWT access and opaque refresh token management.

    All fields support resolution from environment variables prefixed
    with TOKENS_ following the BaseConfig precedence rules.

    Attributes
    ----------
    jwt_secret_key : str
        Secret key used to sign and verify JWT access tokens. Must be
        treated as sensitive data and never logged or exposed in responses.
    jwt_algorithm : str
        Cryptographic algorithm used for JWT signing and verification.
        Default is "HS256".
    access_token_ttl : int
        Lifetime of a JWT access token in seconds. After expiry the client
        must use the refresh token to obtain a new access token. Default
        is 300 (5 minutes).
    refresh_token_ttl : int
        Lifetime of an opaque refresh token in seconds. The token is stored
        in Redis under this TTL and is invalidated on logout. Default is
        2592000 (30 days).
    refresh_token_length : int
        Number of random bytes used to generate the opaque refresh token
        via secrets.token_hex. The resulting hex string is twice this
        length. Must not exceed 383 to keep the Redis key within the
        recommended size limits. Default is 32, producing a 64-character
        token.
    """

    env_prefix: ClassVar[str] = "TOKENS_"

    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_ttl: int = Field(default=300, ge=1)
    refresh_token_ttl: int = Field(default=2592000, ge=1)
    refresh_token_length: int = Field(default=32, ge=1, le=383)


tokens_config = TokensConfig()