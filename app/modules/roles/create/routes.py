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