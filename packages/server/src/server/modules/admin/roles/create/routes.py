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

# packages/server/src/server/modules/admin/roles/create/routes.py
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from postgres_lib import RoleRepository
from auth_lib import PermissionEnum
from .schemas import CreateRoleRequest, CreateRoleResponse
from ..router import roles_admin_router
from .....dependencies import get_async_db_session, require_permission


@roles_admin_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=CreateRoleResponse,
    summary="Create a new role",
    description=(
        "Creates a new role with the provided name. "
        "Returns 409 if a role with the given name already exists. "
        "Requires the roles:create permission."
    ),
)
async def create_role_route(
    body: CreateRoleRequest,
    payload: dict = Depends(require_permission(PermissionEnum.ROLES_CREATE)),
    db: AsyncSession = Depends(get_async_db_session),
) -> CreateRoleResponse:
    """
    Create a new role in the system.

    Parameters
    ----------
    body : CreateRoleRequest
        Request payload containing the name of the role to create.
    payload : dict
        Decoded JWT payload injected by require_permission. Confirms the
        caller holds the roles:create permission.
    db : AsyncSession
        Active async database session injected by get_async_db_session.

    Returns
    -------
    CreateRoleResponse
        Primary key of the newly created role record.

    Raises
    ------
    HTTPException
        409 Conflict if a role with the given name already exists.
    """
    existing = await RoleRepository.get_by_name(db, name=body.name)
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Role with name '{body.name}' already exists.",
        )

    role = await RoleRepository.create(db, obj_data={"name": body.name})
    await db.commit()

    return CreateRoleResponse.model_validate(role)