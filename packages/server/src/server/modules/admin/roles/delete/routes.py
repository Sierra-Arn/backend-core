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

# packages/server/src/server/modules/admin/roles/delete/routes.py
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from postgres_lib import RoleRepository
from auth_lib import PermissionEnum
from ..router import roles_admin_router
from .....dependencies import get_async_db_session, require_permission


@roles_admin_router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a role by primary key",
    description=(
        "Permanently removes the role record with the given id from the system. "
        "All associated permission assignments are deleted automatically via cascade. "
        "Returns 404 if no role exists with that id. "
        "Requires the roles:delete permission."
    ),
)
async def delete_role_route(
    id: int,
    payload: dict = Depends(require_permission(PermissionEnum.ROLES_DELETE)),
    db: AsyncSession = Depends(get_async_db_session),
) -> None:
    """
    Permanently remove a role identified by primary key.

    All associated RolePermission records are deleted automatically via
    the cascade defined on Role.permissions.

    Parameters
    ----------
    id : int
        Primary key of the role to delete.
    payload : dict
        Decoded JWT payload injected by require_permission. Confirms the
        caller holds the roles:delete permission.
    db : AsyncSession
        Active async database session injected by get_async_db_session.

    Raises
    ------
    HTTPException
        404 Not Found if no role exists with the given primary key.
    """
    deleted = await RoleRepository.delete_by_id(db, obj_id=id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role with id {id} does not exist.",
        )
    await db.commit()