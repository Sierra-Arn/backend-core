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

# packages/server/src/server/modules/admin/users/delete/routes.py
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from postgres_lib import UserRepository, PermissionEnum
from ..router import users_admin_router
from .....dependencies import get_async_db_session, require_permission


@users_admin_router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a user by primary key",
    description=(
        "Permanently removes the user record with the given id from the system. "
        "Returns 404 if no user exists with that id. "
        "Requires the users:delete permission."
    ),
)
async def delete_user_route(
    user_id: int,
    payload: dict = Depends(require_permission(PermissionEnum.USERS_DELETE)),
    db: AsyncSession = Depends(get_async_db_session),
) -> None:
    """
    Permanently remove a user record identified by primary key.

    Parameters
    ----------
    user_id : int
        Primary key of the user to delete.
    payload : dict
        Decoded JWT payload injected by require_permission. Confirms the
        caller holds the users:delete permission.
    db : AsyncSession
        Active async database session injected by get_async_db_session.

    Raises
    ------
    HTTPException
        404 Not Found if no user exists with the given primary key.
    """
    deleted = await UserRepository.delete_by_id(db, obj_id=user_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} does not exist.",
        )
    await db.commit()