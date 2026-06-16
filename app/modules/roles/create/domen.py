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

# app/modules/roles/create/domen.py
from fastapi import HTTPException, status
from ....shared.postgres.db import get_async_db_session
from ....shared.postgres.db.repositories import RoleRepository
from .schemas import CreateRoleResponse


async def create_role(name: str) -> CreateRoleResponse:
    """
    Create a new role with the given name.

    Parameters
    ----------
    name : str
        Unique name for the new role.

    Returns
    -------
    CreateRoleResponse
        The newly created role with its auto-generated id.

    Raises
    ------
    HTTPException
        ``409 Conflict`` if a role with the given name already exists.
    """
    
    async with get_async_db_session() as db:
        role_repo = RoleRepository(db)

        if await role_repo.get_by_name(name) is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Role '{name}' already exists.",
            )

        role = await role_repo.create({"name": name})
        await db.commit()

    return CreateRoleResponse(id=role.id, name=role.name)