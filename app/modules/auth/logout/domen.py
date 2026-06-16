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

# app/modules/auth/logout/domen.py
from datetime import datetime, timezone
from fastapi import HTTPException, status
from ....shared.postgres.db import get_async_db_session
from ....shared.postgres.db.repositories import RefreshTokenRepository
from ....shared.redis.db import async_redis_client, add_to_blacklist
from ....shared.auth import decode_access_token


async def logout(access_token: str, refresh_token: str) -> None:
    """
    Invalidate the current session by blacklisting the access token and
    deleting the refresh token from the database.

    Parameters
    ----------
    access_token : str
        The raw JWT access token to blacklist.
    refresh_token : str
        The opaque refresh token to delete from the database.

    Raises
    ------
    HTTPException
        ``401 Unauthorized`` if the access token is invalid or expired.
    """

    try:
        payload = decode_access_token(access_token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token.",
        )

    jti = payload["jti"]
    exp = payload["exp"]
    ttl = int(exp - datetime.now(timezone.utc).timestamp())

    if ttl > 0:
        await add_to_blacklist(
            client=async_redis_client,
            jti=jti,
            ttl_seconds=ttl,
        )

    async with get_async_db_session() as db:
        refresh_token_repo = RefreshTokenRepository(db)
        await refresh_token_repo.delete_by_token(refresh_token)
        await db.commit()