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

# app/modules/account/change_password/domen.py
from datetime import datetime, timezone
from fastapi import HTTPException, status
from ....shared.postgres.db import get_async_db_session
from ....shared.postgres.db.repositories import UserRepository, RefreshTokenRepository
from ....shared.redis.db import async_redis_client, add_to_blacklist
from ....shared.auth import verify_password, hash_password


async def change_password(
    user_id: int,
    current_password: str,
    new_password: str,
    refresh_token: str,
    access_token_jti: str,
    access_token_exp: float,
) -> None:
    """
    Change the authenticated user's password and invalidate the current session.

    Verifies the current password before applying the change. On success,
    the provided refresh token is deleted from the database and the current
    access token is added to the blacklist, terminating the active session.
    Sessions on other devices are not affected.

    Parameters
    ----------
    user_id : int
        Primary key of the authenticated user, extracted from the JWT payload.
    current_password : str
        The user's existing plaintext password for verification.
    new_password : str
        The new plaintext password to hash and store.
    refresh_token : str
        The opaque refresh token of the current session to delete.
    access_token_jti : str
        ``jti`` claim of the current access token. Used as the Redis key
        when blacklisting the token.
    access_token_exp : float
        ``exp`` claim of the current access token as a Unix timestamp.
        Used to calculate the remaining TTL for the blacklist entry.

    Raises
    ------
    HTTPException
        ``401 Unauthorized`` if ``current_password`` does not match the
        stored hash.
        ``409 Conflict`` if ``new_password`` is identical to
        ``current_password``.
    """

    async with get_async_db_session() as db:
        user_repo = UserRepository(db)
        refresh_token_repo = RefreshTokenRepository(db)

        user = await user_repo.get(user_id)

        if not verify_password(current_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Current password is incorrect.",
            )

        await user_repo.update(user_id, {"hashed_password": hash_password(new_password)})
        await refresh_token_repo.delete_by_token(refresh_token)
        await db.commit()

    ttl = int(access_token_exp - datetime.now(timezone.utc).timestamp())
    if ttl > 0:
        await add_to_blacklist(
            client=async_redis_client,
            jti=access_token_jti,
            ttl_seconds=ttl,
        )