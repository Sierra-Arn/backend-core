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

# app/shared/auth/config.py
from typing import ClassVar
from pydantic import Field
from ..base_config import BaseConfig


class AuthenticationConfig(BaseConfig):
    """
    Configuration schema for authentication and token management.

    Attributes
    ----------
    jwt_secret_key : str
        Secret key used to sign and verify JWT access tokens.
    jwt_algorithm : str
        Algorithm used for JWT signing and verification.
        Default is ``"HS256"`` (HMAC with SHA-256).
    access_token_ttl : int
        Lifetime of an access token in seconds.
        Default is ``300`` (5 minutes).
    refresh_token_ttl : int
        Lifetime of a refresh token in seconds.
        Default is ``2592000`` (30 days).
    refresh_token_length : int
        Number of random bytes passed to ``secrets.token_urlsafe()`` when
        generating a new refresh token. The resulting base64url-encoded string
        is always longer than the input byte count by a factor of ~1.33.
        Must not exceed ``383`` to guarantee the encoded output never exceeds
        the ``String(512)`` column constraint in the database.
        Default is ``32`` (produces a 43-character token).
    bcrypt_rounds : int
        Cost factor passed to bcrypt when hashing passwords. Controls the
        number of iterations as ``2 ** bcrypt_rounds``. Higher values increase
        resistance to brute-force attacks at the cost of longer hashing time.
        Default is ``12``, which is the widely accepted production baseline.

    Notes
    -----
    This class inherits from `app.base_config.BaseConfig`.
    For details on configuration loading behavior, see its documentation.
    """

    env_prefix: ClassVar[str] = "AUTHENTICATION_"

    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_ttl: int = Field(default=300, ge=1)
    refresh_token_ttl: int = Field(default=2592000, ge=1)
    refresh_token_length: int = Field(default=32, ge=1, le=383)
    bcrypt_rounds: int = Field(default=12, ge=4, le=31)

    @property
    def password_hash_algorithm(self) -> str:
        """
        Hashing algorithm used for password storage.

        Returns
        -------
        str
            Always returns ``"bcrypt"``.

        Notes
        -----
        Exposed as a read-only property rather than a configurable field
        because changing the hashing algorithm would invalidate all existing
        password hashes stored in the database, requiring a full migration.
        
        Bcrypt is chosen as the fixed algorithm because it is battle-tested,
        and widely supported.
        """

        return "bcrypt"


# Initialize authentication configuration singleton.
# Since authentication settings are static for the application's lifetime
# and any configuration changes require a full application restart,
# it is safe to instantiate the config once at module level and reuse
# it throughout the application as a singleton.
authentication_config = AuthenticationConfig()