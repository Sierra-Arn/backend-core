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

# packages/server/src/server/modules/admin/roles/get/routes.py
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from postgres_lib import RoleRepository
from auth_lib import PermissionEnum
from .schemas import RoleResponse
from ..router import roles_admin_router
from .....dependencies import get_async_db_session, require_permission


@roles_admin_router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=list[RoleResponse],
    summary="Retrieve a paginated list of all roles",
    description=(
        "Returns a paginated list of all defined roles ordered by primary key. "
        "Requires the roles:get_all permission."
    ),
)
async def get_all_roles_route(
    skip: int = 0,
    limit: int = 100,
    payload: dict = Depends(require_permission(PermissionEnum.ROLES_GET_ALL)),
    db: AsyncSession = Depends(get_async_db_session),
) -> list[RoleResponse]:
    """
    Return a paginated list of all defined roles.

    Parameters
    ----------
    skip : int, optional
        Number of records to offset from the beginning of the result set.
        Default is 0.
    limit : int, optional
        Maximum number of records to return. Default is 100.
    payload : dict
        Decoded JWT payload injected by require_permission. Confirms the
        caller holds the roles:get_all permission.
    db : AsyncSession
        Active async database session injected by get_async_db_session.

    Returns
    -------
    list of RoleResponse
        Paginated list of role records ordered by ascending primary key.
    """
    roles = await RoleRepository.get_all(db, skip=skip, limit=limit)
    return [RoleResponse.model_validate(r) for r in roles]


@roles_admin_router.get(
    "/{role_id}",
    status_code=status.HTTP_200_OK,
    response_model=RoleResponse,
    summary="Retrieve a single role by primary key",
    description=(
        "Returns the role record with the given id. "
        "Returns 404 if no role exists with that id. "
        "Requires the roles:get permission."
    ),
)
async def get_role_route(
    role_id: int,
    payload: dict = Depends(require_permission(PermissionEnum.ROLES_GET)),
    db: AsyncSession = Depends(get_async_db_session),
) -> RoleResponse:
    """
    Return a single role identified by primary key.

    Parameters
    ----------
    role_id : int
        Primary key of the role to retrieve.
    payload : dict
        Decoded JWT payload injected by require_permission. Confirms the
        caller holds the roles:get permission.
    db : AsyncSession
        Active async database session injected by get_async_db_session.

    Returns
    -------
    RoleResponse
        Record of the requested role.

    Raises
    ------
    HTTPException
        404 Not Found if no role exists with the given primary key.
    """
    role = await RoleRepository.get_by_id(db, obj_id=role_id)
    if role is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role with id {role_id} does not exist.",
        )
    return RoleResponse.model_validate(role)