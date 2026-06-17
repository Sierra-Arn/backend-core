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

# packages/server/src/server/modules/admin/roles/manage_permissions/routes.py
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from postgres_lib import RoleRepository
from auth_lib import PermissionEnum
from .schemas import AssignPermissionRequest, RevokePermissionRequest
from ..router import roles_admin_router
from .....dependencies import get_async_db_session, require_permission


@roles_admin_router.post(
    "/{role_id}/permissions",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Assign a permission to a role",
    description=(
        "Assigns the specified permission to the role with the given id. "
        "Returns 404 if no role exists with that id. "
        "Returns 409 if the permission is already assigned to the role. "
        "Requires the roles:manage_permissions permission."
    ),
)
async def assign_permission_route(
    role_id: int,
    body: AssignPermissionRequest,
    payload: dict = Depends(require_permission(PermissionEnum.ROLES_MANAGE_PERMISSIONS)),
    db: AsyncSession = Depends(get_async_db_session),
) -> None:
    """
    Assign a permission to a role identified by primary key.

    Parameters
    ----------
    role_id : int
        Primary key of the role receiving the permission.
    body : AssignPermissionRequest
        Request payload containing the permission value to assign.
    payload : dict
        Decoded JWT payload injected by require_permission. Confirms the
        caller holds the roles:manage_permissions permission.
    db : AsyncSession
        Active async database session injected by get_async_db_session.

    Raises
    ------
    HTTPException
        404 Not Found if no role exists with the given primary key.
        409 Conflict if the permission is already assigned to the role.
    """
    role = await RoleRepository.get_by_id(db, obj_id=role_id)
    if role is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role with id {role_id} does not exist.",
        )

    if await RoleRepository.has_permission(db, role_id=role_id, permission=body.permission):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Permission '{body.permission}' is already assigned to role with id {role_id}.",
        )

    await RoleRepository.assign_permission(db, role_id=role_id, permission=body.permission)
    await db.commit()


@roles_admin_router.delete(
    "/{role_id}/permissions",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Revoke a permission from a role",
    description=(
        "Revokes the specified permission from the role with the given id. "
        "Returns 404 if no role exists with that id. "
        "Returns 409 if the permission is not assigned to the role. "
        "Requires the roles:manage_permissions permission."
    ),
)
async def revoke_permission_route(
    role_id: int,
    body: RevokePermissionRequest,
    payload: dict = Depends(require_permission(PermissionEnum.ROLES_MANAGE_PERMISSIONS)),
    db: AsyncSession = Depends(get_async_db_session),
) -> None:
    """
    Revoke a permission from a role identified by primary key.

    Parameters
    ----------
    role_id : int
        Primary key of the role to revoke the permission from.
    body : RevokePermissionRequest
        Request payload containing the permission value to revoke.
    payload : dict
        Decoded JWT payload injected by require_permission. Confirms the
        caller holds the roles:manage_permissions permission.
    db : AsyncSession
        Active async database session injected by get_async_db_session.

    Raises
    ------
    HTTPException
        404 Not Found if no role exists with the given primary key.
        409 Conflict if the permission is not assigned to the role.
    """
    role = await RoleRepository.get_by_id(db, obj_id=role_id)
    if role is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role with id {role_id} does not exist.",
        )

    if not await RoleRepository.has_permission(db, role_id=role_id, permission=body.permission):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Permission '{body.permission}' is not assigned to role with id {role_id}.",
        )

    await RoleRepository.revoke_permission(db, role_id=role_id, permission=body.permission)
    await db.commit()