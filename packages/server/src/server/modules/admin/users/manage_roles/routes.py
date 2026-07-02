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

# packages/server/src/server/modules/admin/users/manage_roles/routes.py
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from postgres_lib import UserRepository, RoleRepository, PermissionEnum
from .schemas import AssignRoleRequest, RevokeRoleRequest
from ..router import users_admin_router
from .....dependencies import get_async_db_session, require_permission


@users_admin_router.post(
    "/{user_id}/roles",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Assign a role to a user",
    description=(
        "Assigns the specified role to the user with the given id. "
        "Returns 404 if the user or role does not exist. "
        "Returns 409 if the role is already assigned to the user. "
        "Requires the users:manage_roles permission."
    ),
)
async def assign_role_route(
    user_id: int,
    body: AssignRoleRequest,
    payload: dict = Depends(require_permission(PermissionEnum.USERS_MANAGE_ROLES)),
    db: AsyncSession = Depends(get_async_db_session),
) -> None:
    """
    Assign a role to a user identified by primary key.

    Parameters
    ----------
    user_id : int
        Primary key of the user receiving the role.
    body : AssignRoleRequest
        Request payload containing the role_id to assign.
    payload : dict
        Decoded JWT payload injected by require_permission. Confirms the
        caller holds the users:manage_roles permission.
    db : AsyncSession
        Active async database session injected by get_async_db_session.

    Raises
    ------
    HTTPException
        404 Not Found if the user or role does not exist.
        409 Conflict if the role is already assigned to the user.
    """
    user = await UserRepository.get_by_id(db, obj_id=user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} does not exist.",
        )

    role = await RoleRepository.get_by_id(db, obj_id=body.role_id)
    if role is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role with id {body.role_id} does not exist.",
        )

    if await UserRepository.has_role(db, user_id=user_id, role_id=body.role_id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Role with id {body.role_id} is already assigned to user with id {user_id}.",
        )

    await UserRepository.assign_role(db, user_id=user_id, role_id=body.role_id)
    await db.commit()


@users_admin_router.delete(
    "/{user_id}/roles",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Revoke a role from a user",
    description=(
        "Revokes the specified role from the user with the given id. "
        "Returns 404 if the user or role does not exist. "
        "Returns 409 if the role is not assigned to the user. "
        "Requires the users:manage_roles permission."
    ),
)
async def revoke_role_route(
    user_id: int,
    body: RevokeRoleRequest,
    payload: dict = Depends(require_permission(PermissionEnum.USERS_MANAGE_ROLES)),
    db: AsyncSession = Depends(get_async_db_session),
) -> None:
    """
    Revoke a role from a user identified by primary key.

    Parameters
    ----------
    user_id : int
        Primary key of the user to revoke the role from.
    body : RevokeRoleRequest
        Request payload containing the role_id to revoke.
    payload : dict
        Decoded JWT payload injected by require_permission. Confirms the
        caller holds the users:manage_roles permission.
    db : AsyncSession
        Active async database session injected by get_async_db_session.

    Raises
    ------
    HTTPException
        404 Not Found if the user or role does not exist.
        409 Conflict if the role is not assigned to the user.
    """
    user = await UserRepository.get_by_id(db, obj_id=user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} does not exist.",
        )

    role = await RoleRepository.get_by_id(db, obj_id=body.role_id)
    if role is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role with id {body.role_id} does not exist.",
        )

    if not await UserRepository.has_role(db, user_id=user_id, role_id=body.role_id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Role with id {body.role_id} is not assigned to user with id {user_id}.",
        )

    await UserRepository.revoke_role(db, user_id=user_id, role_id=body.role_id)
    await db.commit()