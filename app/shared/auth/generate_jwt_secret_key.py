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