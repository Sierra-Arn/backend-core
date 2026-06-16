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

# app/modules/roles/create/routes.py
from fastapi import Depends, status
from .schemas import CreateRoleRequest, CreateRoleResponse
from .domen import create_role
from ..router import roles_router
from ....shared.auth.dependencies import require_permission


@roles_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=CreateRoleResponse,
    summary="Create a new role",
    description=(
        "Creates a new role with the given name. "
        "Restricted to users with the ``roles:create`` permission. "
        "Returns ``409`` if a role with the given name already exists."
    ),
)
async def create_role_route(
    body: CreateRoleRequest,
    payload: dict = Depends(require_permission("roles:create")),
) -> CreateRoleResponse:
    return await create_role(name=body.name)