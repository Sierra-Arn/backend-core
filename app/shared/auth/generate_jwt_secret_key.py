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

# app/shared/auth/generate_jwt_secret_key.py

"""
Utility script for generating cryptographically secure secret keys.

Run directly to print a new JWT secret key suitable for use as AUTHENTICATION_JWT_SECRET_KEY:

    python -m app.shared.auth.generate_jwt_secret_key
"""

import secrets


def generate_jwt_secret_key() -> str:
    """
    Generate a cryptographically secure random secret key for JWT signing.

    Uses ``secrets.token_urlsafe`` to produce a URL-safe base64-encoded
    string derived from 32 bytes of OS-level randomness, yielding
    approximately 43 characters of high-entropy suitable for HMAC-SHA256.

    Returns
    -------
    str
        A URL-safe base64-encoded random string suitable for use as
        ``AUTHENTICATION_JWT_SECRET_KEY`` in the application configuration.
    """
    return secrets.token_urlsafe(32)

if __name__ == "__main__":
    print(generate_jwt_secret_key())