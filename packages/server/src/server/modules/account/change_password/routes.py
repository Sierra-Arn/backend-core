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

# packages/server/src/server/modules/account/change_password/routes.py
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from postgres_lib import UserRepository
from auth_lib import PasswordRepository
from redis_lib import RefreshTokenRepository
from .schemas import ChangePasswordRequest
from ..router import account_router
from ....dependencies import get_async_db_session, get_current_user


@account_router.patch(
    "/change-password",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Change the authenticated user's password",
    description=(
        "Verifies the current password, replaces it with the new one, and "
        "revokes the provided refresh token to terminate the current session. "
        "Returns 401 if the current password is incorrect."
    ),
)
async def change_password_route(
    body: ChangePasswordRequest,
    payload: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db_session),
) -> None:
    """
    Change the password of the currently authenticated user and revoke
    the current session.

    Parameters
    ----------
    body : ChangePasswordRequest
        Request payload containing the current password, new password,
        and refresh token to revoke after the change.
    payload : dict
        Decoded JWT payload injected by get_current_user. Provides the
        user_id via the sub claim.
    db : AsyncSession
        Active async database session injected by get_async_db_session.

    Raises
    ------
    HTTPException
        401 Unauthorized if the current password does not match the
        stored bcrypt hash.
    """
    user = await UserRepository.get_by_id(db, obj_id=int(payload["sub"]))

    if not PasswordRepository.verify(body.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect.",
        )

    await UserRepository.update_by_id(
        db,
        obj_id=user.id,
        obj_data={"hashed_password": PasswordRepository.hash(body.new_password)},
    )
    await RefreshTokenRepository.revoke(token=body.refresh_token)
    await db.commit()