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

# app/shared/auth/password.py
import bcrypt
from .config import authentication_config


def hash_password(plain_password: str) -> str:
    """
    Produce a bcrypt hash of the given plaintext password.

    A random salt is generated internally by bcrypt on every call,
    so two calls with the same password will always produce different hashes.

    Parameters
    ----------
    plain_password : str
        The raw password string supplied by the user during registration
        or a password-change request.

    Returns
    -------
    str
        A bcrypt hash string in Modular Crypt Format
        (e.g. ``$2b$12$...``), safe to store directly in the
        ``users.hashed_password`` column.
    """

    salt = bcrypt.gensalt(rounds=authentication_config.bcrypt_rounds)
    return bcrypt.hashpw(plain_password.encode(), salt).decode()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify that a plaintext password matches a stored bcrypt hash.

    Parameters
    ----------
    plain_password : str
        The raw password string supplied by the user during a login
        or credential-verification request.
    hashed_password : str
        The bcrypt hash previously stored in the database.

    Returns
    -------
    bool
        ``True`` if the password matches the hash; ``False`` otherwise.

    Notes
    -----
    ``bcrypt.checkpw`` is constant-time with respect to the hash
    comparison step, which prevents timing-based side-channel attacks
    that could reveal whether a supplied password is "close" to the
    correct one.
    """
    
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())