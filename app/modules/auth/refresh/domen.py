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

# app/modules/auth/refresh/domen.py
from datetime import datetime, timezone, timedelta
from fastapi import HTTPException, status
from ....shared.postgres.db import get_async_db_session
from ....shared.postgres.db.repositories import (
    UserRepository,
    RefreshTokenRepository
)
from ....shared.auth import (
    authentication_config,
    create_access_token,
    create_refresh_token
)


async def refresh(refresh_token: str) -> dict:
    """
    Issue a new access/refresh token pair and invalidate the old one.

    Validates the incoming refresh token, performs token rotation —
    deleting the old refresh token and issuing a new pair — so that
    a stolen token cannot be reused after the legitimate client has
    already refreshed.

    Parameters
    ----------
    refresh_token : str
        The opaque refresh token previously issued by ``login`` or ``refresh``.

    Returns
    -------
    dict
        Dictionary containing the new ``access_token`` and ``refresh_token``.

    Raises
    ------
    HTTPException
        ``401 Unauthorized`` if the refresh token does not exist or has expired.
    """
    
    async with get_async_db_session() as db:
        user_repo = UserRepository(db)
        refresh_token_repo = RefreshTokenRepository(db)

        token_record = await refresh_token_repo.get_by_token(refresh_token)
        if token_record is None or token_record.expires_at < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token.",
            )

        user = await user_repo.get(
            user_id=token_record.user_id,
            load_roles = True,
            load_permissions = True
        )
        permissions = list({
            perm.permission
            for role in user.roles
            for perm in role.permissions
        })
        now = datetime.now(timezone.utc)
        new_access_token = create_access_token(user_id=user.id, permissions=permissions, now=now)
        new_refresh_token = create_refresh_token()

        await refresh_token_repo.delete_by_token(refresh_token)
        await refresh_token_repo.create({
            "user_id": user.id,
            "token": new_refresh_token,
            "expires_at": now + timedelta(seconds=authentication_config.refresh_token_ttl),
        })
        await db.commit()

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
    }