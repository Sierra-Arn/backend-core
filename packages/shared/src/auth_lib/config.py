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

# packages/shared/src/auth_lib/config.py
from typing import ClassVar, Final
from pydantic import Field
from base_lib import BaseConfig


class AuthenticationConfig(BaseConfig):
    """
    Configuration schema for authentication and token management.

    Attributes
    ----------
    jwt_secret_key : str
        Secret key used to sign and verify JWT access tokens.
    jwt_algorithm : str
        Algorithm used for JWT signing and verification.
        Default is HS256 (HMAC with SHA-256).
    access_token_ttl : int
        Lifetime of an access token in seconds. Default is 300 (5 minutes).
    refresh_token_ttl : int
        Lifetime of a refresh token in seconds. Default is 2592000 (30 days).
    refresh_token_length : int
        Number of random bytes passed to secrets.token_urlsafe when generating
        a new refresh token. The resulting base64url-encoded string is always
        longer than the input byte count by a factor of approximately 1.33.
        Default is 32, which produces a 43-character token.
    bcrypt_rounds : int
        Cost factor passed to bcrypt when hashing passwords. Controls the
        number of iterations as 2 ** bcrypt_rounds. Higher values increase
        resistance to brute-force attacks at the cost of longer hashing time.
        Default is 12, which is the widely accepted production baseline.
    _password_hash_algorithm : Final[str]
        Hashing algorithm used for password storage. Fixed to bcrypt and never
        configurable because changing the algorithm would invalidate all existing
        password hashes in the database, requiring a full migration.
    """

    env_prefix: ClassVar[str] = "AUTHENTICATION_"

    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_ttl: int = Field(default=300, ge=1)
    refresh_token_ttl: int = Field(default=2592000, ge=1)
    refresh_token_length: int = Field(default=32, ge=1, le=383)
    bcrypt_rounds: int = Field(default=12, ge=4, le=31)
    _password_hash_algorithm: Final[str] = "bcrypt"


auth_config = AuthenticationConfig()