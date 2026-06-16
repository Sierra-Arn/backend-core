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

# app/modules/auth/login/domen.py
from datetime import datetime, timezone, timedelta
from fastapi import HTTPException, status
from ....shared.postgres.db import get_async_db_session
from ....shared.postgres.db.repositories import (
    UserRepository,
    RefreshTokenRepository
)
from ....shared.auth import (
    authentication_config,
    verify_password,
    create_access_token,
    create_refresh_token
)

async def login(email: str, password: str) -> dict:
    """
    Authenticate a user and issue a new access/refresh token pair.

    Parameters
    ----------
    email : str
        Email address of the account.
    password : str
        Plaintext password to verify against the stored hash.

    Returns
    -------
    dict
        Dictionary containing ``access_token`` and ``refresh_token``.

    Raises
    ------
    HTTPException
        ``401 Unauthorized`` if the email does not exist or the password
        is incorrect. A deliberately generic message is used to avoid
        leaking whether the email is registered.
    """
    
    async with get_async_db_session() as db:
        user_repo = UserRepository(db)
        refresh_token_repo = RefreshTokenRepository(db)

        user = await user_repo.get_by_email(
            email=email,
            load_roles = True,
            load_permissions = True
        )
        if user is None or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password.",
            )

        permissions = list({
            perm.permission
            for role in user.roles
            for perm in role.permissions
        })
        now = datetime.now(timezone.utc)
        access_token = create_access_token(user_id=user.id, permissions=permissions, now=now)
        refresh_token = create_refresh_token()

        await refresh_token_repo.create({
            "user_id": user.id,
            "token": refresh_token,
            "expires_at": now + timedelta(seconds=authentication_config.refresh_token_ttl),
        })
        await db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
    }